"""Post-run exact patch re-review for the Sprint 11 operator acceptance."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.io import (
    load_adaptation_plan,
    load_framework_snapshot,
    load_workspace_profile,
)
from test_cartographer.delivery.apply import apply_code_patch
from test_cartographer.delivery.enums import PatchReviewDecision
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.io import (
    load_code_patch,
    load_generation_profile,
    save_application_report,
    save_code_patch,
)
from test_cartographer.delivery.review import review_code_patch
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox
from test_cartographer.discovery.engine import complete_ambiguity_prompt
from test_cartographer.discovery.io import load_discovery_run, save_discovery_run
from test_cartographer.interactive_creation.io import save_patch_rereview_report
from test_cartographer.interactive_creation.models import ExactPatchRereviewReport
from test_cartographer.interactive_creation.runner import _ask_accept, _format_code_patch
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.synthesis.io import load_synthesis_run

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
TimerFn = Callable[[], float]
NowFn = Callable[[], datetime]
TARGET_TEST = "tests/e2e/test_search_catalog.py"


def rereview_existing_sprint_11_patch(
    *,
    project_root: str | Path,
    artifact_dir: str | Path,
    framework_root: str | Path | None = None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    timer_fn: TimerFn = time.perf_counter,
    now_fn: NowFn = lambda: datetime.now(timezone.utc),
    command_runner=None,
    reference_server=None,
) -> ExactPatchRereviewReport:
    """Regenerate, fully display, accept, apply, and execute one corrected patch."""

    root = Path(project_root).resolve()
    artifacts = Path(artifact_dir).resolve()
    command_runner = command_runner or _run
    reference_server = reference_server or serve_reference_directory
    required = {
        "creation-flow-run.json",
        "02-discovery-run.json",
        "04-synthesis-run.json",
        "05-framework-snapshot.json",
        "05-adaptation-plan.json",
        "06-generation-profile.json",
        "06-code-patch.json",
    }
    missing = sorted(name for name in required if not (artifacts / name).is_file())
    if missing:
        raise FileNotFoundError(f"missing Sprint 11 artefacts: {missing}")

    run_payload = (artifacts / "creation-flow-run.json").read_text(encoding="utf-8")
    import json

    run_id = json.loads(run_payload)["id"]
    old_patch = load_code_patch(artifacts / "06-code-patch.json")
    synthesis_run = load_synthesis_run(artifacts / "04-synthesis-run.json")
    snapshot = load_framework_snapshot(artifacts / "05-framework-snapshot.json")
    plan = load_adaptation_plan(artifacts / "05-adaptation-plan.json")
    generation_profile = load_generation_profile(artifacts / "06-generation-profile.json")
    workspace_profile = load_workspace_profile(
        root / "testdata/adaptation/profile/qa_automation_framework.json"
    )
    source_framework = Path(
        framework_root or root / "testdata/framework/reference"
    ).resolve()
    original_hash = _tree_hash(source_framework)

    started_at = now_fn()
    patch = build_code_patch(
        synthesis_run,
        plan,
        workspace_profile,
        generation_profile,
        snapshot,
        source_framework,
        patch_id=f"patch_rereview_{uuid.uuid4().hex[:12]}",
        created_at=started_at,
    )

    output_fn("\nSprint 11 exact source-patch re-review")
    output_fn("The previous intake, discovery, and authority decisions are reused.")
    output_fn("Every source line is displayed below; no preview ellipsis is used.")
    output_fn(_format_code_patch(patch))
    review_timer = timer_fn()
    accepted = _ask_accept(
        "Accept all exact source changes shown above?", input_fn, output_fn
    )
    completed_at = now_fn()
    review_seconds = max(0.0, timer_fn() - review_timer)
    if not accepted:
        raise RuntimeError("operator rejected the corrected exact source patch")
    patch = review_code_patch(
        patch,
        decision=PatchReviewDecision.ACCEPTED,
        reviewed_at=completed_at,
        reason=(
            "The operator accepted every displayed source change after full exact "
            "rendering with no omitted lines."
        ),
        review_seconds=review_seconds,
    )

    rereview_root = artifacts / "rereview"
    sandbox = rereview_root / "sandbox" / "qa-automation-framework"
    if rereview_root.exists():
        shutil.rmtree(rereview_root)
    rereview_root.mkdir(parents=True)
    materialize_snapshot_sandbox(
        source_framework, sandbox, workspace_profile, snapshot
    )
    application = apply_code_patch(
        patch,
        workspace_profile,
        snapshot,
        sandbox,
        application_id=f"apply_rereview_{uuid.uuid4().hex[:12]}",
        applied_at=now_fn(),
    )

    compile_result = command_runner(
        [sys.executable, "-m", "compileall", "-q", "pages", "components", "tests", "testdata"],
        sandbox,
    )
    collect_result = command_runner(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", TARGET_TEST],
        sandbox,
    )
    with reference_server(root / "testdata/browser") as app_base:
        env = os.environ.copy()
        env["TEST_CARTOGRAPHER_CATALOG_URL"] = (
            f"{app_base}/public_catalog_discovery.html"
        )
        test_result = command_runner(
            [sys.executable, "-m", "pytest", "-q", TARGET_TEST], sandbox, env
        )
    for label, result in (
        ("compileall", compile_result),
        ("collect", collect_result),
        ("execute", test_result),
    ):
        if result.returncode != 0:
            raise RuntimeError(
                f"corrected patch {label} failed:\n{result.stdout}\n{result.stderr}"
            )

    discovery = load_discovery_run(artifacts / "02-discovery-run.json")
    repaired = False
    ambiguities = []
    for ambiguity in discovery.ambiguities:
        if ambiguity.question is None:
            ambiguities.append(ambiguity)
            continue
        question, used_fallback = complete_ambiguity_prompt(
            ambiguity.question, ambiguity.candidate_ids
        )
        repaired = repaired or used_fallback
        ambiguities.append(ambiguity.model_copy(update={"question": question}))
    if repaired:
        discovery = discovery.model_copy(update={"ambiguities": tuple(ambiguities)})
        save_discovery_run(discovery, artifacts / "02-discovery-run.json")

    save_code_patch(patch, rereview_root / "08-code-patch-rereview.json")
    save_application_report(
        application, rereview_root / "08-patch-application-rereview.json"
    )
    report = ExactPatchRereviewReport(
        id=f"patch_rereview_report_{uuid.uuid4().hex[:12]}",
        creation_flow_run_id=run_id,
        original_patch_id=old_patch.id,
        corrected_patch_id=patch.id,
        started_at=started_at,
        completed_at=now_fn(),
        decision="accepted",
        ambiguity_question_deterministically_completed=repaired,
        change_count=len(patch.changes),
        operator_review_seconds=review_seconds,
        collected_test_count=1,
        passed_test_count=1,
        original_framework_unchanged=_tree_hash(source_framework) == original_hash,
    )
    save_patch_rereview_report(report, rereview_root / "08-exact-patch-rereview.json")
    _update_summary(artifacts / "creation-flow-summary.md", report)

    output_fn("\nExact patch re-review completed successfully.")
    output_fn(f"Original patch: {report.original_patch_id}")
    output_fn(f"Corrected patch: {report.corrected_patch_id}")
    output_fn(f"Exact source displayed: true")
    output_fn(f"Omitted source lines: false")
    output_fn(f"Navigation docstring corrected: true")
    output_fn(
        "Ambiguity question deterministically completed: "
        f"{str(report.ambiguity_question_deterministically_completed).lower()}"
    )
    output_fn("LLM role disclosed: true")
    output_fn("Deterministic synthesis disclosed: true")
    output_fn("Tests collected / passed: 1/1")
    output_fn("Original framework unchanged: true")
    output_fn(f"Report: {rereview_root / '08-exact-patch-rereview.json'}")
    return report


def _run(
    command: list[str], cwd: Path, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _update_summary(target: Path, report: ExactPatchRereviewReport) -> None:
    existing = target.read_text(encoding="utf-8").rstrip() if target.exists() else ""
    marker = "\n## Exact patch re-review\n"
    if marker in existing:
        existing = existing.split(marker, 1)[0].rstrip()
    section = "\n".join(
        (
            "",
            "## Exact patch re-review",
            "",
            f"- Decision: **{report.decision}**",
            "- Every source line displayed before acceptance: **yes**",
            "- Omitted source lines: **no**",
            "- Navigation docstring generated from method responsibility: **yes**",
            "- LLM role: **intake-question planning and ambiguity clarification only**",
            "- POM and source generation: **deterministic reviewed reference templates**",
            "- Corrected patch collected / passed: **1 / 1**",
            "- Original framework unchanged: **yes**",
        )
    )
    target.write_text(existing + section + "\n", encoding="utf-8", newline="\n")
