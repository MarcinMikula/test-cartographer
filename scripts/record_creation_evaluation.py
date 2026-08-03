"""Record bounded creation-lifecycle measurements from verification outputs."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.io import load_adaptation_plan
from test_cartographer.delivery.evaluation import build_creation_evaluation
from test_cartographer.delivery.io import (
    load_application_report,
    load_code_patch,
    save_creation_evaluation,
)
from test_cartographer.delivery.models import VerificationResult
from test_cartographer.synthesis.io import load_synthesis_run


def _result(name: str, command: str, output_path: Path, exit_code: int, seconds: float) -> VerificationResult:
    output = output_path.read_text(encoding="utf-8", errors="replace")
    return VerificationResult(
        name=name,
        command=command,
        exit_code=exit_code,
        duration_seconds=seconds,
        output_sha256=hashlib.sha256(output.encode("utf-8")).hexdigest(),
        passed=exit_code == 0,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--patch", required=True, type=Path)
    parser.add_argument("--application", required=True, type=Path)
    parser.add_argument("--evaluation", required=True, type=Path)
    parser.add_argument("--evaluation-id", required=True)
    parser.add_argument("--target-test", required=True)
    parser.add_argument("--compile-output", required=True, type=Path)
    parser.add_argument("--compile-exit-code", required=True, type=int)
    parser.add_argument("--compile-seconds", required=True, type=float)
    parser.add_argument("--collect-output", required=True, type=Path)
    parser.add_argument("--collect-exit-code", required=True, type=int)
    parser.add_argument("--collect-seconds", required=True, type=float)
    parser.add_argument("--test-output", required=True, type=Path)
    parser.add_argument("--test-exit-code", required=True, type=int)
    parser.add_argument("--test-seconds", required=True, type=float)
    parser.add_argument("--collected-test-count", required=True, type=int)
    parser.add_argument("--passed-test-count", required=True, type=int)
    parser.add_argument("--time-to-first-runnable-test-seconds", required=True, type=float)
    parser.add_argument("--original-framework-unchanged", action="store_true")
    parser.add_argument("--correction", action="append", default=[])
    args = parser.parse_args()

    results = (
        _result(
            "compileall",
            "python -m compileall -q pages components tests testdata",
            args.compile_output,
            args.compile_exit_code,
            args.compile_seconds,
        ),
        _result(
            "collect_target",
            f"python -m pytest --collect-only -q {args.target_test}",
            args.collect_output,
            args.collect_exit_code,
            args.collect_seconds,
        ),
        _result(
            "execute_target",
            f"python -m pytest -q {args.target_test}",
            args.test_output,
            args.test_exit_code,
            args.test_seconds,
        ),
    )
    evaluation = build_creation_evaluation(
        load_synthesis_run(args.run),
        load_adaptation_plan(args.plan),
        load_code_patch(args.patch),
        load_application_report(args.application),
        evaluation_id=args.evaluation_id,
        completed_at=datetime.now(timezone.utc),
        target_test=args.target_test,
        collected_test_count=args.collected_test_count,
        passed_test_count=args.passed_test_count,
        verification_results=results,
        verification_seconds=args.compile_seconds + args.collect_seconds + args.test_seconds,
        time_to_first_runnable_test_seconds=args.time_to_first_runnable_test_seconds,
        original_framework_unchanged=args.original_framework_unchanged,
        corrections=tuple(args.correction),
    )
    save_creation_evaluation(evaluation, args.evaluation)
    print(f"Created creation evaluation: {args.evaluation}")
    print(f"Status: {evaluation.status.value}")
    return 0 if evaluation.status.value == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
