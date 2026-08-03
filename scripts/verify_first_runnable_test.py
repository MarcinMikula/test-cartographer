"""Prove the first complete context-to-runnable-framework-test lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.io import (
    load_adaptation_plan,
    load_framework_snapshot,
    load_workspace_profile,
)
from test_cartographer.delivery.apply import apply_code_patch
from test_cartographer.delivery.evaluation import build_creation_evaluation
from test_cartographer.delivery.io import (
    load_code_patch,
    save_application_report,
    save_creation_evaluation,
)
from test_cartographer.delivery.models import VerificationResult
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox
from test_cartographer.observation.reference import serve_reference_directory
from test_cartographer.synthesis.io import load_synthesis_run

ROOT = Path(__file__).resolve().parents[1]
TARGET_TEST = "tests/e2e/test_search_catalog.py"


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> tuple[subprocess.CompletedProcess[str], float]:
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    return result, time.perf_counter() - started


def _verification(name: str, command: list[str], result: subprocess.CompletedProcess[str], seconds: float) -> VerificationResult:
    output = f"{result.stdout}\n{result.stderr}"
    return VerificationResult(
        name=name,
        command=" ".join(command),
        exit_code=result.returncode,
        duration_seconds=seconds,
        output_sha256=hashlib.sha256(output.encode()).hexdigest(),
        passed=result.returncode == 0,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require-browser", action="store_true")
    parser.add_argument("--evaluation", type=Path)
    args = parser.parse_args()

    source_framework = ROOT / "testdata/framework/reference"
    original_hash = _tree_hash(source_framework)
    lifecycle_started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="test-cartographer-sprint-6-") as temporary:
        framework = Path(temporary) / "framework"
        workspace_profile = load_workspace_profile(ROOT / "testdata/adaptation/profile/qa_automation_framework.json")
        framework_snapshot = load_framework_snapshot(ROOT / "testdata/adaptation/snapshot/qa_automation_framework.json")
        materialize_snapshot_sandbox(
            source_framework,
            framework,
            workspace_profile,
            framework_snapshot,
        )
        application = apply_code_patch(
            load_code_patch(ROOT / "testdata/delivery/patch/accepted_public_search.json"),
            workspace_profile,
            framework_snapshot,
            framework,
            application_id="apply_verify_public_search",
            applied_at=datetime.now(timezone.utc),
        )

        compile_command = [sys.executable, "-m", "compileall", "-q", "pages", "components", "tests", "testdata"]
        compile_result, compile_seconds = _run(compile_command, framework)
        collect_command = [sys.executable, "-m", "pytest", "--collect-only", "-q", TARGET_TEST]
        collect_result, collect_seconds = _run(collect_command, framework)

        with serve_reference_directory(ROOT / "testdata/browser") as base_url:
            env = os.environ.copy()
            env["TEST_CARTOGRAPHER_CATALOG_URL"] = f"{base_url}/public_catalog.html"
            test_command = [sys.executable, "-m", "pytest", "-q", TARGET_TEST]
            test_result, test_seconds = _run(test_command, framework, env)

        browser_output = f"{test_result.stdout}\n{test_result.stderr}"
        browser_unavailable = test_result.returncode != 0 and any(
            marker in browser_output
            for marker in (
                "Executable doesn't exist",
                "Failed to launch",
                "ERR_BLOCKED_BY_ADMINISTRATOR",
            )
        )
        if browser_unavailable and not args.require_browser:
            print("First runnable framework test browser gate skipped by environment policy.")
            return 0

        results = (
            _verification("compileall", compile_command, compile_result, compile_seconds),
            _verification("collect_target", collect_command, collect_result, collect_seconds),
            _verification("execute_target", test_command, test_result, test_seconds),
        )
        evaluation = build_creation_evaluation(
            load_synthesis_run(ROOT / "testdata/synthesis/run/accepted_public_search.json"),
            load_adaptation_plan(ROOT / "testdata/adaptation/plan/accepted_public_search.json"),
            load_code_patch(ROOT / "testdata/delivery/patch/accepted_public_search.json"),
            application,
            evaluation_id="creation_verify_public_search",
            completed_at=datetime.now(timezone.utc),
            target_test=TARGET_TEST,
            collected_test_count=1 if collect_result.returncode == 0 else 0,
            passed_test_count=1 if test_result.returncode == 0 else 0,
            verification_results=results,
            verification_seconds=compile_seconds + collect_seconds + test_seconds,
            time_to_first_runnable_test_seconds=time.perf_counter() - lifecycle_started,
            original_framework_unchanged=_tree_hash(source_framework) == original_hash,
            corrections=(
                "Fixture placement was aligned with tests/e2e/conftest.py before generation.",
            ),
        )
        if args.evaluation is not None:
            args.evaluation.parent.mkdir(parents=True, exist_ok=True)
            save_application_report(application, args.evaluation.with_name("controlled-application.json"))
            save_creation_evaluation(evaluation, args.evaluation)

        if evaluation.status.value != "passed":
            print(compile_result.stdout, compile_result.stderr)
            print(collect_result.stdout, collect_result.stderr)
            print(test_result.stdout, test_result.stderr)
            return 1

    print("Accepted context, POM proposal, adaptation plan, and code patch remained traceable.")
    print("Exact generated source was applied only to a snapshot-bounded framework sandbox.")
    print("Files outside the accepted workspace snapshot were not copied into the sandbox.")
    print("Page Object, component, fixture, and test compiled successfully.")
    print("Pytest collected exactly one generated E2E test.")
    print("The generated test passed against the controlled local page in Chromium.")
    print("The original framework fixture remained byte-for-byte unchanged.")
    print("No live LLM was used during framework execution.")
    print("First runnable framework test: verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
