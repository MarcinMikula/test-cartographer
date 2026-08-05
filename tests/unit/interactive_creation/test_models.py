import pytest
from pydantic import ValidationError

from test_cartographer.creation_flow.models import CreationFlowRun
from test_cartographer.interactive_creation.enums import InteractiveSessionState


def test_complete_operator_session_records_real_human_boundary(operator_session) -> None:
    assert operator_session.state is InteractiveSessionState.COMPLETE
    assert operator_session.fixture_answers_used is False
    assert operator_session.interactive_human_trigger_used is True
    assert operator_session.headed_browser_used is True
    assert operator_session.initial_trigger_count == 1
    assert operator_session.answer_count == 9
    assert operator_session.confirmation_count == 1
    assert operator_session.handoff_confirmation_count == 1
    assert operator_session.ambiguity_selection_count == 1
    assert operator_session.review_decision_count == 4
    assert operator_session.execution_trigger_count == 1
    assert len(operator_session.actions) == 18
    assert operator_session.active_seconds == 18.0


def test_complete_operator_session_requires_headed_browser(operator_session) -> None:
    payload = operator_session.model_dump(mode="python")
    payload["headed_browser_used"] = False
    with pytest.raises(ValidationError, match="headed browser"):
        type(operator_session).model_validate(payload)


def test_creation_run_cannot_be_fixture_and_interactive(passed_creation_run) -> None:
    payload = passed_creation_run.model_dump(mode="python")
    payload["interactive_human_used_during_verifier"] = True
    with pytest.raises(ValidationError, match="fixture-assisted and interactive"):
        CreationFlowRun.model_validate(payload)


def test_exact_patch_rereview_report_requires_complete_proof() -> None:
    from datetime import datetime, timedelta, timezone

    from test_cartographer.interactive_creation.models import ExactPatchRereviewReport

    started = datetime(2026, 8, 5, 16, 0, tzinfo=timezone.utc)
    report = ExactPatchRereviewReport(
        id="patch_rereview_report_test",
        creation_flow_run_id="creation_flow_interactive_test",
        original_patch_id="patch_original",
        corrected_patch_id="patch_corrected",
        started_at=started,
        completed_at=started + timedelta(seconds=5),
        decision="accepted",
        ambiguity_question_deterministically_completed=True,
        change_count=4,
        operator_review_seconds=4.0,
        collected_test_count=1,
        passed_test_count=1,
    )
    assert report.exact_source_displayed is True
    assert report.omitted_source_lines is False
    assert report.deterministic_synthesis_disclosed is True
