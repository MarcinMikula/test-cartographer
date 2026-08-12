"""Deterministic assessment of the real operator boundary."""

from test_cartographer.context.models import ContractModel, Identifier
from test_cartographer.creation_flow.assessment import assess_creation_flow
from test_cartographer.creation_flow.models import CreationFlowRun
from test_cartographer.interactive_creation.enums import InteractiveSessionState
from test_cartographer.interactive_creation.models import (
    InteractiveCreationProfile,
    InteractiveOperatorSession,
)


class InteractiveCreationAssessment(ContractModel):
    session_id: Identifier
    human_trigger_verified: bool
    external_user_demo_ready: bool
    blockers: tuple[Identifier, ...] = ()


def assess_interactive_creation(
    session: InteractiveOperatorSession,
    run: CreationFlowRun,
    profile: InteractiveCreationProfile,
) -> InteractiveCreationAssessment:
    blockers: list[str] = []
    engine = assess_creation_flow(run)
    if session.state is not InteractiveSessionState.COMPLETE:
        blockers.append("operator_session_not_complete")
    if not session.interactive_human_trigger_used:
        blockers.append("interactive_human_trigger_missing")
    if session.initial_trigger_count < 1:
        blockers.append("real_initial_request_missing")
    if session.fixture_answers_used:
        blockers.append("fixture_answers_used")
    if profile.require_headed_browser and not session.headed_browser_used:
        blockers.append("headed_browser_not_used")
    if session.answer_count < profile.minimum_intake_answers:
        blockers.append("insufficient_real_intake_answers")
    if session.confirmation_count < profile.minimum_intake_confirmations:
        blockers.append("insufficient_real_confirmations")
    if session.handoff_confirmation_count < 1:
        blockers.append("synthesis_handoff_confirmation_missing")
    if session.review_decision_count < profile.minimum_review_decisions:
        blockers.append("real_review_decisions_missing")
    if session.execution_trigger_count < 1:
        blockers.append("real_execution_trigger_missing")
    if not engine.creation_mechanics_verified:
        blockers.append("creation_mechanics_not_verified")
    if not run.interactive_human_used_during_verifier:
        blockers.append("creation_run_not_marked_interactive")
    if run.fixture_assisted_reference_demo:
        blockers.append("creation_run_still_fixture_assisted")
    return InteractiveCreationAssessment(
        session_id=session.id,
        human_trigger_verified=not blockers,
        external_user_demo_ready=not blockers and engine.ready_for_external_user_demo,
        blockers=tuple(blockers),
    )
