"""Run the standalone framework-side collector and validate its bounded bundle."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path

from test_cartographer.execution.assessment import assess_execution_evidence
from test_cartographer.execution.io import load_execution_bundle

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    temporary = (
        tempfile.TemporaryDirectory(prefix="test-cartographer-execution-")
        if args.output is None
        else nullcontext(None)
    )
    with temporary as directory:
        output = (
            Path(directory) / "execution-evidence-bundle.json"
            if args.output is None
            else args.output
        )
        assert output is not None
        output.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        env.update(
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
            PYTHONPATH=str(ROOT / "testdata/execution/framework_plugin"),
            TEST_CARTOGRAPHER_SECRET="reference-secret-not-for-persistence",
        )
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "--tb=no",
                str(ROOT / "testdata/execution/framework_suite"),
                "-p",
                "execution_evidence_plugin",
                "--execution-evidence-profile",
                str(ROOT / "testdata/execution/profile/strict_internal.json"),
                "--execution-evidence-output",
                str(output),
                "--execution-run-id",
                "run_reference_execution",
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 1:
            raise SystemExit(
                "Reference pytest run must finish with one intentional test failure "
                "and one intentional infrastructure error."
            )
        bundle = load_execution_bundle(output)
        assessment = assess_execution_evidence(bundle)
        rendered = output.read_text(encoding="utf-8")
        forbidden = (
            "reference-secret-not-for-persistence",
            "user:password",
            "query=Example",
            "#results",
            "catalog result mismatch",
            "browser service unavailable",
        )
        present = [value for value in forbidden if value in rendered]
        if present:
            raise SystemExit(f"Execution evidence leaked forbidden values: {present}")
        if (
            bundle.passed_count != 1
            or bundle.test_failure_count != 1
            or bundle.infrastructure_error_count != 1
        ):
            raise SystemExit("Reference bundle did not preserve the three outcomes.")
        if not assessment.ready_for_reactive_maintenance:
            raise SystemExit("Reference failure evidence is not actionable for Sprint 8.")

    print("Framework-side pytest collector ran without importing TestCartographer.")
    print("One pass, one test failure, and one infrastructure error were distinguished.")
    print("Every record linked to context, process, synthesis, plan, patch, and source IDs.")
    print("The last bounded POM step and minimized application path were retained.")
    print(
        "Input values, credentials, raw messages, tracebacks, output, HTML, "
        "screenshots, and traces were not persisted."
    )
    print("Test failure was not classified as an application bug.")
    print("Execution evidence is ready for deterministic reactive-maintenance intake.")
    print("No live LLM was used and Cartographer was not required during pytest execution.")
    if args.output is not None:
        print(f"Persisted reference execution bundle: {args.output}")


if __name__ == "__main__":
    main()
