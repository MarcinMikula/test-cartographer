import hashlib
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.adaptation.enums import AdaptationTargetKind
from test_cartographer.delivery.enums import CreationEvaluationStatus
from test_cartographer.delivery.evaluation import build_creation_evaluation
from test_cartographer.delivery.models import CreationEvaluation, VerificationResult


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

def test_evaluation_allows_componentless_pass_when_proposal_requires_no_component(
    accepted_run,
    accepted_plan,
    accepted_patch,
    application_report,
):
    assert accepted_run.proposal is not None
    componentless_proposal = accepted_run.proposal.model_copy(update={"components": ()})
    componentless_run = accepted_run.model_copy(update={"proposal": componentless_proposal})
    componentless_patch = accepted_patch.model_copy(
        update={
            "changes": tuple(
                change
                for change in accepted_patch.changes
                if change.target_kind is not AdaptationTargetKind.COMPONENT
            )
        }
    )

    evaluation = build_creation_evaluation(
        componentless_run,
        accepted_plan,
        componentless_patch,
        application_report,
        evaluation_id="creation_test_componentless_passed",
        completed_at=datetime(2026, 8, 12, 17, 45, tzinfo=timezone.utc),
        target_test="tests/e2e/test_driving_licence_codes.py",
        collected_test_count=1,
        passed_test_count=1,
        verification_results=(
            _verification("compileall", True),
            _verification("collect", True),
            _verification("pytest", True),
        ),
        verification_seconds=1.5,
        time_to_first_runnable_test_seconds=60.0,
        original_framework_unchanged=True,
    )

    assert evaluation.status is CreationEvaluationStatus.PASSED
    assert evaluation.component_required is False
    assert evaluation.component_generated is False


def test_passed_evaluation_rejects_missing_required_component(passed_evaluation):
    payload = passed_evaluation.model_dump(mode="python")
    payload["status"] = CreationEvaluationStatus.PASSED
    payload["component_required"] = True
    payload["component_generated"] = False

    with pytest.raises(
        ValidationError,
        match="passed creation evaluation requires all execution and architecture checks",
    ):
        CreationEvaluation.model_validate(payload)

def test_legacy_evaluation_defaults_component_requirement_to_true(passed_evaluation):
    payload = passed_evaluation.model_dump(mode="python")
    payload.pop("component_required")

    restored = CreationEvaluation.model_validate(payload)

    assert restored.component_required is True
