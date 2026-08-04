import pytest
from pydantic import ValidationError

from test_cartographer.creation_flow.assessment import assess_creation_flow


def test_passed_fixture_run_verifies_mechanics_but_not_external_demo(passed_creation_run) -> None:
    report = assess_creation_flow(passed_creation_run)
    assert report.creation_mechanics_verified
    assert report.ready_for_human_trigger_integration
    assert not report.ready_for_external_user_demo
    assert report.mechanics_blockers == ()
    assert report.external_demo_blockers == ("interactive_human_trigger_missing",)


def test_passed_run_requires_matching_human_action_total(passed_creation_run) -> None:
    payload = passed_creation_run.model_dump(mode="python")
    payload["total_human_action_count"] = 21
    with pytest.raises(ValidationError, match="total_human_action_count"):
        type(passed_creation_run).model_validate(payload)


def test_assessment_blocks_missing_passing_test(passed_creation_run) -> None:
    payload = passed_creation_run.model_dump(mode="python")
    payload["status"] = "failed"
    payload["passed_test_count"] = 0
    run = type(passed_creation_run).model_validate(payload)
    report = assess_creation_flow(run)
    assert not report.creation_mechanics_verified
    assert not report.ready_for_human_trigger_integration
    assert not report.ready_for_external_user_demo
    assert "flow_not_passed" in report.mechanics_blockers
    assert "runnable_test_missing" in report.mechanics_blockers
    assert "creation_mechanics_not_verified" in report.external_demo_blockers
