"""Controlled reference runner for human-triggered reactive maintenance."""

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

from test_cartographer.adaptation.io import load_workspace_profile
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox
from test_cartographer.context.enums import ActionKind, LocatorStrategy, SensitivityLevel
from test_cartographer.discovery.capture import capture_process_discovery
from test_cartographer.discovery.enums import DiscoveryProviderKind
from test_cartographer.discovery.models import (
    DiscoveryProfile,
    DiscoveryTarget,
    ProcessDiscoveryPlan,
    ProcessDiscoveryRun,
)
from test_cartographer.execution.io import load_execution_bundle
from test_cartographer.execution.models import ExecutionEvidenceBundle
from test_cartographer.interactive_creation.browser import open_interactive_discovery
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.reactive_maintenance.assessment import assess_failure_for_maintenance
from test_cartographer.reactive_maintenance.enums import (
    MaintenanceActionKind,
    MaintenanceDecision,
    MaintenanceDisposition,
    MaintenanceStatus,
)
from test_cartographer.reactive_maintenance.io import (
    load_maintenance_profile,
    save_maintenance_diagnosis,
    save_maintenance_evidence_assessment,
    save_maintenance_patch,
    save_maintenance_run,
)
from test_cartographer.reactive_maintenance.models import (
    MaintenanceActionRecord,
    MaintenanceCandidate,
    MaintenanceDiagnosis,
    MaintenanceSourcePatch,
    ReactiveMaintenanceProfile,
    ReactiveMaintenanceRun,
)

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
TimerFn = Callable[[], float]
NowFn = Callable[[], datetime]


class MaintenanceRejected(RuntimeError):
    """Raised when the operator rejects one bounded maintenance boundary."""


def collect_framework_evidence(
    framework_root: str | Path,
    *,
    application_url: str,
    execution_profile_path: str | Path,
    output_path: str | Path,
    run_id: str,
) -> tuple[subprocess.CompletedProcess[str], ExecutionEvidenceBundle]:
    """Run one framework test with the standalone evidence collector."""

    root = Path(framework_root).resolve()
    output = Path(output_path).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    project_root = Path(__file__).resolve().parents[3]
    plugin_root = project_root / "testdata/execution/framework_plugin"
    env = os.environ.copy()
    for inherited_name in (
        "PYTEST_ADDOPTS",
        "PYTEST_CURRENT_TEST",
        "PYTEST_PLUGINS",
    ):
        env.pop(inherited_name, None)
    env.update(
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        PYTHONPATH=os.pathsep.join((str(plugin_root), str(root))),
        PYTHONUTF8="1",
        TEST_CARTOGRAPHER_CATALOG_URL=application_url,
    )
    target_test = root / "tests/e2e/test_search_catalog.py"
    config_path = root / "pytest.ini"
    if not config_path.is_file():
        raise RuntimeError(f"framework pytest configuration is missing: {config_path}")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
            "-c",
            str(config_path),
            "--rootdir",
            str(root),
            str(target_test),
            "-p",
            "execution_evidence_plugin",
            "--execution-evidence-profile",
            str(Path(execution_profile_path).resolve()),
            "--execution-evidence-output",
            str(output),
            "--execution-run-id",
            run_id,
        ],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if not output.is_file():
        raise RuntimeError(
            "framework execution did not produce an evidence bundle:\n"
            f"stdout={result.stdout}\nstderr={result.stderr}"
        )
    return result, load_execution_bundle(output)


def _bounded_process_text(value: str, *, limit: int = 3000) -> str:
    """Return bounded diagnostics without persisting them in evidence artifacts."""

    normalized = value.strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit] + "\n...[diagnostic output truncated]"


def _require_expected_test_failure(
    result: subprocess.CompletedProcess[str],
    bundle: ExecutionEvidenceBundle,
    *,
    label: str,
) -> None:
    """Require one semantic test failure and no pass/infrastructure outcome.

    The evidence bundle is the source of truth for failure classification.
    The process must still be non-zero, but the validator does not assume that
    every supported Windows/pytest wrapper encodes the failure as exactly 1.
    """

    valid = (
        result.returncode != 0
        and bundle.passed_count == 0
        and bundle.test_failure_count == 1
        and bundle.infrastructure_error_count == 0
        and len(bundle.records) == 1
    )
    if valid:
        return
    raise RuntimeError(
        f"{label} did not prove exactly one clean test failure; "
        f"exit={result.returncode}; "
        f"passed={bundle.passed_count}; "
        f"test_failures={bundle.test_failure_count}; "
        f"infrastructure_errors={bundle.infrastructure_error_count}; "
        f"records={len(bundle.records)}; "
        f"stdout={_bounded_process_text(result.stdout)!r}; "
        f"stderr={_bounded_process_text(result.stderr)!r}"
    )


def build_maintenance_discovery(
    application_url: str,
    profile: ReactiveMaintenanceProfile,
) -> tuple[ProcessDiscoveryPlan, DiscoveryProfile]:
    plan = ProcessDiscoveryPlan(
        id="maintenance_discovery_plan",
        context_id="ctx_cb1897ffad97",
        process_id="proc_target",
        page_id="page_catalog",
        page_name="Public catalog changed reference",
        route="/public_catalog_changed.html",
        source_url=application_url,
        component_ids=("comp_catalog_search",),
        targets=(
            DiscoveryTarget(
                id="target_maintenance_submit",
                element_id=profile.target_element_id,
                owner_id="comp_catalog_search",
                name="Search action",
                action_kind=ActionKind.CLICK,
                expected_roles=(profile.expected_semantic_role,),
            ),
            DiscoveryTarget(
                id="target_maintenance_results",
                element_id="el_search_results",
                owner_id="page_catalog",
                name="Catalog results",
                action_kind=ActionKind.READ,
                expected_roles=("list",),
                outcome_target=True,
            ),
        ),
        sensitivity=SensitivityLevel.INTERNAL,
    )
    discovery_profile = DiscoveryProfile(
        id="maintenance_discovery_replay",
        provider=DiscoveryProviderKind.REPLAY,
        model="deterministic-maintenance-reobservation",
        base_url="replay://local",
        max_elements_scanned=20,
        max_candidates_per_target=4,
        minimum_candidate_score=45,
        ambiguity_score_delta=3,
    )
    return plan, discovery_profile


def capture_maintenance_candidates(
    application_url: str,
    profile: ReactiveMaintenanceProfile,
    *,
    headed: bool,
    executable_path: str | None = None,
):
    plan, discovery_profile = build_maintenance_discovery(application_url, profile)
    captured_at = datetime.now(timezone.utc)
    if headed:
        return open_interactive_discovery(
            plan,
            discovery_profile,
            run_id=f"maintenance_discovery_{uuid.uuid4().hex[:10]}",
            captured_at=captured_at,
            executable_path=executable_path,
        )
    return capture_process_discovery(
        plan,
        discovery_profile,
        run_id=f"maintenance_discovery_{uuid.uuid4().hex[:10]}",
        captured_at=captured_at,
        headed=False,
        executable_path=executable_path,
    )


def matching_maintenance_candidates(
    run: ProcessDiscoveryRun,
    profile: ReactiveMaintenanceProfile,
    record_id: str,
) -> tuple[MaintenanceCandidate, ...]:
    old_present = any(
        locator.strategy == profile.old_locator_strategy
        and locator.value == profile.old_locator_value
        and locator.match_count > 0
        for candidate in run.candidates
        for locator in candidate.locator_candidates
    )
    values: list[MaintenanceCandidate] = []
    for candidate in run.candidates:
        if (
            candidate.semantic_role != profile.expected_semantic_role
            or candidate.semantic_name != profile.expected_semantic_name
        ):
            continue
        test_ids = [
            locator
            for locator in candidate.locator_candidates
            if locator.strategy is LocatorStrategy.TEST_ID and locator.match_count == 1
        ]
        if not test_ids:
            continue
        locator = test_ids[0]
        values.append(
            MaintenanceCandidate(
                id=candidate.id,
                semantic_role=candidate.semantic_role,
                semantic_name=candidate.semantic_name,
                locator_strategy=locator.strategy,
                locator_value=locator.value,
                match_count=locator.match_count,
                enabled=candidate.enabled,
                attributes=tuple(
                    f"{item.name}={item.value}" for item in candidate.attributes
                ),
                source_record_id=record_id,
                old_locator_absent=not old_present,
                deterministic_match=True,
            )
        )
    return tuple(values)


def build_maintenance_diagnosis(
    profile: ReactiveMaintenanceProfile,
    bundle: ExecutionEvidenceBundle,
    selected: MaintenanceCandidate,
    *,
    candidate_count: int,
    diagnosis_id: str | None = None,
) -> MaintenanceDiagnosis:
    assessment = assess_failure_for_maintenance(bundle, profile)
    if assessment.disposition is not MaintenanceDisposition.REOBSERVATION_REQUIRED:
        raise ValueError("maintenance diagnosis requires evidence ready for re-observation")
    if assessment.record_id != selected.source_record_id:
        raise ValueError("selected candidate does not belong to the failure record")
    if not selected.old_locator_absent:
        raise ValueError("reference repair requires proof that the old locator is absent")
    return MaintenanceDiagnosis(
        id=diagnosis_id or f"diagnosis_{uuid.uuid4().hex[:12]}",
        profile_id=profile.id,
        bundle_id=bundle.id,
        record_id=assessment.record_id,
        created_at=datetime.now(timezone.utc),
        target_source_path=profile.target_source_path,
        target_symbol=profile.target_symbol,
        old_locator_strategy=profile.old_locator_strategy,
        old_locator_value=profile.old_locator_value,
        selected_candidate=selected,
        candidate_count=candidate_count,
    )


def build_maintenance_patch(
    framework_root: str | Path,
    profile: ReactiveMaintenanceProfile,
    diagnosis: MaintenanceDiagnosis,
    *,
    patch_id: str | None = None,
) -> MaintenanceSourcePatch:
    root = Path(framework_root).resolve()
    target = root.joinpath(*profile.target_source_path.split("/"))
    if not target.is_file() or target.is_symlink():
        raise ValueError("maintenance target must be an existing non-symlink file")
    before_bytes = target.read_bytes()
    before = before_bytes.decode("utf-8")
    old_single = f"get_by_test_id('{profile.old_locator_value}')"
    old_double = f'get_by_test_id("{profile.old_locator_value}")'
    occurrences = before.count(old_single) + before.count(old_double)
    if occurrences != 1:
        raise ValueError("maintenance patch requires exactly one stale locator occurrence")
    replacement = f"get_by_test_id('{diagnosis.selected_candidate.locator_value}')"
    after = before.replace(old_single, replacement).replace(old_double, replacement)
    compile(after, profile.target_source_path, "exec")
    before_hash = hashlib.sha256(before_bytes).hexdigest()
    after_hash = hashlib.sha256(after.encode("utf-8")).hexdigest()
    return MaintenanceSourcePatch(
        id=patch_id or f"maintenance_patch_{uuid.uuid4().hex[:12]}",
        diagnosis_id=diagnosis.id,
        profile_id=profile.id,
        created_at=datetime.now(timezone.utc),
        target_path=profile.target_source_path,
        symbol_name=profile.target_symbol,
        expected_before_sha256=before_hash,
        old_locator_value=profile.old_locator_value,
        new_locator_value=diagnosis.selected_candidate.locator_value,
        full_source=after,
        full_source_sha256=after_hash,
        expected_after_sha256=after_hash,
    )


def apply_patch_to_fresh_sandbox(
    framework_root: str | Path,
    workspace_profile_path: str | Path,
    patch: MaintenanceSourcePatch,
    sandbox_root: str | Path,
) -> Path:
    source = Path(framework_root).resolve()
    sandbox = Path(sandbox_root).resolve()
    profile = load_workspace_profile(workspace_profile_path)
    before_snapshot = inspect_framework(
        source,
        profile,
        snapshot_id=f"maintenance_before_{uuid.uuid4().hex[:8]}",
        captured_at=datetime.now(timezone.utc),
    )
    if sandbox.exists():
        shutil.rmtree(sandbox)
    materialize_snapshot_sandbox(source, sandbox, profile, before_snapshot)
    target = sandbox.joinpath(*patch.target_path.split("/"))
    actual_before = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual_before != patch.expected_before_sha256:
        raise ValueError("sandbox target does not match reviewed patch precondition")
    target.write_text(patch.full_source, encoding="utf-8", newline="\n")
    actual_after = hashlib.sha256(target.read_bytes()).hexdigest()
    if actual_after != patch.expected_after_sha256:
        raise ValueError("sandbox target does not match reviewed patch result")
    source_after = inspect_framework(
        source,
        profile,
        snapshot_id=f"maintenance_source_after_{uuid.uuid4().hex[:8]}",
        captured_at=datetime.now(timezone.utc),
    )
    if source_after.root_fingerprint != before_snapshot.root_fingerprint:
        raise ValueError("original framework changed during sandbox maintenance")
    return sandbox


def _record_action(
    actions: list[MaintenanceActionRecord],
    kind: MaintenanceActionKind,
    target_id: str,
    decision: str,
    *,
    started_at: datetime,
    completed_at: datetime,
    active_seconds: float,
) -> None:
    actions.append(
        MaintenanceActionRecord(
            sequence=len(actions) + 1,
            kind=kind,
            target_id=target_id,
            decision=decision,
            started_at=started_at,
            completed_at=completed_at,
            active_seconds=active_seconds,
        )
    )


def _ask_accept(
    prompt: str,
    kind: MaintenanceActionKind,
    target_id: str,
    actions: list[MaintenanceActionRecord],
    *,
    input_fn: InputFn,
    output_fn: OutputFn,
    now_fn: NowFn,
    timer_fn: TimerFn,
) -> None:
    while True:
        started_at = now_fn()
        started = timer_fn()
        raw = input_fn(f"{prompt} [A]ccept / [R]eject: ").strip().upper()
        completed_at = now_fn()
        elapsed = max(0.0, timer_fn() - started)
        if raw not in {"A", "R"}:
            output_fn("Enter A to accept or R to reject.")
            continue
        decision = "accepted" if raw == "A" else "rejected"
        _record_action(
            actions,
            kind,
            target_id,
            decision,
            started_at=started_at,
            completed_at=completed_at,
            active_seconds=elapsed,
        )
        if raw == "R":
            raise MaintenanceRejected(f"operator rejected {target_id}")
        return


def _format_candidates(candidates: tuple[MaintenanceCandidate, ...]) -> str:
    lines = []
    for item in candidates:
        attrs = ", ".join(item.attributes) or "no bounded attributes"
        lines.append(
            f"  {item.id}: {item.semantic_role} / {item.semantic_name} / "
            f"{item.locator_strategy.value}={item.locator_value} / {attrs}"
        )
    return "\n".join(lines)


def _select_candidate(
    candidates: tuple[MaintenanceCandidate, ...],
    actions: list[MaintenanceActionRecord],
    *,
    input_fn: InputFn,
    output_fn: OutputFn,
    now_fn: NowFn,
    timer_fn: TimerFn,
) -> MaintenanceCandidate:
    allowed = {item.id: item for item in candidates}
    while True:
        started_at = now_fn()
        started = timer_fn()
        raw = input_fn("Select current submit candidate ID: ").strip()
        completed_at = now_fn()
        elapsed = max(0.0, timer_fn() - started)
        selected = allowed.get(raw)
        if selected is None:
            output_fn(f"Choose one of: {', '.join(sorted(allowed))}")
            continue
        _record_action(
            actions,
            MaintenanceActionKind.CANDIDATE_SELECTION,
            "search_submit_candidate",
            selected.id,
            started_at=started_at,
            completed_at=completed_at,
            active_seconds=elapsed,
        )
        return selected


def _write_summary(run: ReactiveMaintenanceRun, path: Path) -> None:
    path.write_text(
        "\n".join(
            (
                "# Reactive Maintenance Flow summary",
                "",
                f"- Run: `{run.id}`",
                f"- Status: `{run.status.value}`",
                "- Failed test is treated as evidence, not an application-bug diagnosis.",
                "- Failure classification and candidate discovery are deterministic.",
                "- LLM role: none in Sprint 12 reactive maintenance.",
                "- Candidate authority: real operator selection in a headed browser.",
                "- Patch authority: full exact source reviewed by the operator.",
                "- Application boundary: isolated sandbox only.",
                f"- Before failures: `{run.failed_test_count_before}`",
                f"- After tests passed: `{run.passed_test_count_after}/{run.collected_test_count_after}`",
                f"- Original framework unchanged: `{str(run.original_framework_unchanged).lower()}`",
                "- Measured comparative savings: `false`",
                "",
            )
        ),
        encoding="utf-8",
        newline="\n",
    )


def run_human_triggered_reactive_maintenance(
    *,
    maintenance_profile_path: str | Path,
    execution_profile_path: str | Path,
    workspace_profile_path: str | Path,
    framework_root: str | Path,
    application_root: str | Path,
    output_dir: str | Path,
    executable_path: str | None = None,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    now_fn: NowFn = lambda: datetime.now(timezone.utc),
    timer_fn: TimerFn = time.perf_counter,
) -> ReactiveMaintenanceRun:
    """Run the controlled real-operator maintenance slice."""

    profile = load_maintenance_profile(maintenance_profile_path)
    source = Path(framework_root).resolve()
    output = Path(output_dir).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    started_at = now_fn()
    actions: list[MaintenanceActionRecord] = []

    output_fn("TestCartographer — human-triggered Reactive Maintenance Flow")
    output_fn("The accepted project/process context is reused; bootstrap questions are not repeated.")
    output_fn("A failed test is evidence, not a diagnosis or an application-bug claim.")
    _ask_accept(
        "Start bounded maintenance from the existing framework test?",
        MaintenanceActionKind.INITIAL_TRIGGER,
        "maintenance_start",
        actions,
        input_fn=input_fn,
        output_fn=output_fn,
        now_fn=now_fn,
        timer_fn=timer_fn,
    )

    source_target = source.joinpath(*profile.target_source_path.split("/"))
    original_target_hash = hashlib.sha256(source_target.read_bytes()).hexdigest()
    with serve_reference_directory(application_root) as base_url:
        application_url = f"{base_url}/public_catalog_changed.html"
        before_result, before_bundle = collect_framework_evidence(
            source,
            application_url=application_url,
            execution_profile_path=execution_profile_path,
            output_path=output / "01-before-execution-evidence.json",
            run_id=f"maintenance_before_{uuid.uuid4().hex[:10]}",
        )
        _require_expected_test_failure(
            before_result,
            before_bundle,
            label="controlled pre-repair run",
        )
        assessment = assess_failure_for_maintenance(before_bundle, profile)
        save_maintenance_evidence_assessment(
            assessment, output / "02-maintenance-evidence-assessment.json"
        )
        output_fn("")
        output_fn("Execution evidence assessment")
        output_fn(f"Outcome: test_failure ({before_bundle.test_failure_count})")
        output_fn(f"Infrastructure errors: {before_bundle.infrastructure_error_count}")
        output_fn(f"Disposition: {assessment.disposition.value}")
        output_fn(f"Complete traceability: {str(assessment.complete_traceability).lower()}")
        output_fn(f"Matching bounded last step: {str(assessment.matching_last_step).lower()}")
        output_fn("Application bug claimed: false")
        output_fn("Stale locator claimed before re-observation: false")
        if not assessment.ready_for_reobservation or assessment.record_id is None:
            raise RuntimeError("execution evidence is not ready for bounded re-observation")
        _ask_accept(
            "Proceed to current-page re-observation?",
            MaintenanceActionKind.EVIDENCE_REVIEW,
            assessment.record_id,
            actions,
            input_fn=input_fn,
            output_fn=output_fn,
            now_fn=now_fn,
            timer_fn=timer_fn,
        )

        with capture_maintenance_candidates(
            application_url,
            profile,
            headed=True,
            executable_path=executable_path,
        ) as browser_view:
            candidates = matching_maintenance_candidates(
                browser_view.run, profile, assessment.record_id
            )
            if not candidates:
                raise RuntimeError("re-observation found no bounded repair candidates")
            browser_view.focus_candidates(tuple(item.id for item in candidates))
            output_fn("")
            output_fn("Current visible candidates with the expected role and name:")
            output_fn(_format_candidates(candidates))
            output_fn(f"Old locator `{profile.old_locator_value}` currently present: false")
            selected = _select_candidate(
                candidates,
                actions,
                input_fn=input_fn,
                output_fn=output_fn,
                now_fn=now_fn,
                timer_fn=timer_fn,
            )

        diagnosis = build_maintenance_diagnosis(
            profile,
            before_bundle,
            selected,
            candidate_count=len(candidates),
        )
        save_maintenance_diagnosis(diagnosis, output / "03-maintenance-diagnosis.json")
        patch = build_maintenance_patch(source, profile, diagnosis)
        save_maintenance_patch(patch, output / "04-maintenance-patch-pending.json")

        output_fn("")
        output_fn("Exact reactive-maintenance source patch")
        output_fn(f"Target: {patch.target_path}::{patch.symbol_name}")
        output_fn(f"Before SHA-256: {patch.expected_before_sha256}")
        output_fn(f"After SHA-256:  {patch.expected_after_sha256}")
        output_fn("Every source line follows; no preview ellipsis is used.")
        output_fn("=" * 72)
        output_fn(patch.full_source.rstrip("\n"))
        output_fn("=" * 72)
        review_timer = timer_fn()
        _ask_accept(
            "Accept the exact maintenance source shown above?",
            MaintenanceActionKind.PATCH_REVIEW,
            patch.id,
            actions,
            input_fn=input_fn,
            output_fn=output_fn,
            now_fn=now_fn,
            timer_fn=timer_fn,
        )
        review_seconds = max(0.0, timer_fn() - review_timer)
        patch = patch.model_copy(
            update={
                "status": MaintenanceStatus.PASSED,
                "decision": MaintenanceDecision.ACCEPTED,
                "exact_source_displayed": True,
                "reviewed_at": now_fn(),
                "review_seconds": review_seconds,
            }
        )
        save_maintenance_patch(patch, output / "04-maintenance-patch-accepted.json")

        _ask_accept(
            "Apply the reviewed patch to a fresh sandbox and rerun the test?",
            MaintenanceActionKind.EXECUTION_TRIGGER,
            "maintenance_rerun",
            actions,
            input_fn=input_fn,
            output_fn=output_fn,
            now_fn=now_fn,
            timer_fn=timer_fn,
        )
        sandbox = apply_patch_to_fresh_sandbox(
            source,
            workspace_profile_path,
            patch,
            output / "sandbox/qa-automation-framework",
        )
        after_result, after_bundle = collect_framework_evidence(
            sandbox,
            application_url=application_url,
            execution_profile_path=execution_profile_path,
            output_path=output / "05-after-execution-evidence.json",
            run_id=f"maintenance_after_{uuid.uuid4().hex[:10]}",
        )
        if (
            after_result.returncode != 0
            or after_bundle.passed_count != 1
            or after_bundle.test_failure_count != 0
            or after_bundle.infrastructure_error_count != 0
        ):
            raise RuntimeError(
                "post-repair test did not pass cleanly; "
                f"exit={after_result.returncode} stdout={after_result.stdout} stderr={after_result.stderr}"
            )

    if hashlib.sha256(source_target.read_bytes()).hexdigest() != original_target_hash:
        raise RuntimeError("original framework target changed during maintenance")
    completed_at = now_fn()
    run = ReactiveMaintenanceRun(
        id=f"maintenance_run_{uuid.uuid4().hex[:12]}",
        profile_id=profile.id,
        status=MaintenanceStatus.PASSED,
        started_at=started_at,
        completed_at=completed_at,
        source_execution_bundle_id=before_bundle.id,
        source_failure_record_id=assessment.record_id,
        diagnosis_id=diagnosis.id,
        patch_id=patch.id,
        before_execution_bundle_id=before_bundle.id,
        after_execution_bundle_id=after_bundle.id,
        actions=tuple(actions),
        candidate_count=len(candidates),
        selected_candidate_id=selected.id,
        failed_test_count_before=before_bundle.test_failure_count,
        infrastructure_error_count_before=before_bundle.infrastructure_error_count,
        collected_test_count_after=len(after_bundle.records),
        passed_test_count_after=after_bundle.passed_count,
    )
    save_maintenance_run(run, output / "reactive-maintenance-run.json")
    _write_summary(run, output / "reactive-maintenance-summary.md")
    output_fn("")
    output_fn("Reactive Maintenance Flow completed successfully.")
    output_fn(f"Real operator actions: {run.operator_action_count}")
    output_fn(f"Failure before / pass after: {run.failed_test_count_before} / {run.passed_test_count_after}")
    output_fn("Application bug claimed: false")
    output_fn("Live LLM used: false")
    output_fn("Exact full patch reviewed: true")
    output_fn("Patch applied only to sandbox: true")
    output_fn("Original framework unchanged: true")
    output_fn(f"Artifacts: {output}")
    return run


def run_scripted_maintenance_mechanics(
    *,
    maintenance_profile_path: str | Path,
    execution_profile_path: str | Path,
    workspace_profile_path: str | Path,
    framework_root: str | Path,
    application_root: str | Path,
    output_dir: str | Path,
    executable_path: str | None = None,
) -> None:
    """Verify the engine without claiming a real operator acceptance artefact."""

    profile = load_maintenance_profile(maintenance_profile_path)
    source = Path(framework_root).resolve()
    output = Path(output_dir).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    source_target = source.joinpath(*profile.target_source_path.split("/"))
    original = hashlib.sha256(source_target.read_bytes()).hexdigest()
    with serve_reference_directory(application_root) as base_url:
        application_url = f"{base_url}/public_catalog_changed.html"
        before_result, before_bundle = collect_framework_evidence(
            source,
            application_url=application_url,
            execution_profile_path=execution_profile_path,
            output_path=output / "before.json",
            run_id="maintenance_scripted_before",
        )
        _require_expected_test_failure(
            before_result,
            before_bundle,
            label="scripted maintenance precondition",
        )
        assessment = assess_failure_for_maintenance(before_bundle, profile)
        if before_bundle.infrastructure_error_count:
            raise RuntimeError("browser unavailable during scripted framework setup")
        if assessment.disposition is not MaintenanceDisposition.REOBSERVATION_REQUIRED:
            raise RuntimeError("scripted evidence was not ready for re-observation")
        discovery = capture_maintenance_candidates(
            application_url,
            profile,
            headed=False,
            executable_path=executable_path,
        )
        candidates = matching_maintenance_candidates(
            discovery, profile, assessment.record_id or "missing_record"
        )
        selected = next(
            (item for item in candidates if item.locator_value == "catalog-search-submit"),
            None,
        )
        if selected is None:
            raise RuntimeError("scripted re-observation did not find the changed submit locator")
        diagnosis = build_maintenance_diagnosis(
            profile, before_bundle, selected, candidate_count=len(candidates)
        )
        patch = build_maintenance_patch(source, profile, diagnosis)
        patch = patch.model_copy(
            update={
                "status": MaintenanceStatus.PASSED,
                "decision": MaintenanceDecision.ACCEPTED,
                "exact_source_displayed": True,
                "reviewed_at": datetime.now(timezone.utc),
                "review_seconds": 0.0,
            }
        )
        sandbox = apply_patch_to_fresh_sandbox(
            source,
            workspace_profile_path,
            patch,
            output / "sandbox",
        )
        after_result, after_bundle = collect_framework_evidence(
            sandbox,
            application_url=application_url,
            execution_profile_path=execution_profile_path,
            output_path=output / "after.json",
            run_id="maintenance_scripted_after",
        )
        if after_result.returncode != 0 or after_bundle.passed_count != 1:
            raise RuntimeError("scripted repaired test did not pass")
    current = hashlib.sha256(source_target.read_bytes()).hexdigest()
    if current != original:
        raise RuntimeError("scripted maintenance modified the original framework")
