import hashlib
from datetime import datetime, timezone

from test_cartographer.delivery.enums import CreationEvaluationStatus
from test_cartographer.delivery.evaluation import build_creation_evaluation
from test_cartographer.delivery.models import VerificationResult


def _verification(name: str, passed: bool) -> VerificationResult:
    output = f"{name}:{passed}"
    return VerificationResult(
        name=name,
        command=f"python -m {name}",
        exit_code=0 if passed else 1,
        duration_seconds=0.5,
        output_sha256=hashlib.sha256(output.encode()).hexdigest(),
        passed=passed,
    )


def test_evaluation_passes_only_after_collection_execution_and_architecture_checks(
    accepted_run,
    accepted_plan,
    accepted_patch,
    application_report,
):
    evaluation = build_creation_evaluation(
        accepted_run,
        accepted_plan,
        accepted_patch,
        application_report,
        evaluation_id="creation_test_passed",
        completed_at=datetime(2026, 8, 2, 13, 30, tzinfo=timezone.utc),
        target_test="tests/e2e/test_search_catalog.py",
        collected_test_count=1,
        passed_test_count=1,
        verification_results=(_verification("compileall", True), _verification("pytest", True)),
        verification_seconds=1.0,
        time_to_first_runnable_test_seconds=60.0,
        original_framework_unchanged=True,
    )
    assert evaluation.status is CreationEvaluationStatus.PASSED
    assert evaluation.live_llm_used is False
    assert evaluation.llm_call_count == 0


def test_evaluation_remains_failed_when_target_test_fails(
    accepted_run,
    accepted_plan,
    accepted_patch,
    application_report,
):
    evaluation = build_creation_evaluation(
        accepted_run,
        accepted_plan,
        accepted_patch,
        application_report,
        evaluation_id="creation_test_failed",
        completed_at=datetime(2026, 8, 2, 13, 30, tzinfo=timezone.utc),
        target_test="tests/e2e/test_search_catalog.py",
        collected_test_count=1,
        passed_test_count=0,
        verification_results=(_verification("compileall", True), _verification("pytest", False)),
        verification_seconds=1.0,
        time_to_first_runnable_test_seconds=60.0,
        original_framework_unchanged=True,
    )
    assert evaluation.status is CreationEvaluationStatus.FAILED
