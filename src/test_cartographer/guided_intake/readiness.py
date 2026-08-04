"""Deterministic readiness report for the handoff to guided discovery."""

from __future__ import annotations

from pydantic import computed_field

from test_cartographer.context.models import ContractModel, Identifier
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.guided_intake.enums import GuidedIntakeRunState
from test_cartographer.guided_intake.models import GuidedIntakeRun
from test_cartographer.intake.models import IntakeSession
from test_cartographer.intake.rules import assess_intake, list_questions


class GuidedIntakeReadiness(ContractModel):
    context_id: Identifier
    session_complete: bool
    human_intake_complete: bool
    remaining_question_count: int
    provider_turn_count: int
    live_provider_used: bool
    full_adaptation_blocker_count: int

    @computed_field
    @property
    def ready_for_guided_discovery(self) -> bool:
        return (
            self.session_complete
            and self.human_intake_complete
            and self.remaining_question_count == 0
            and self.provider_turn_count > 0
        )


def assess_guided_intake(
    session: IntakeSession,
    run: GuidedIntakeRun,
) -> GuidedIntakeReadiness:
    intake = assess_intake(session.context)
    full = assess_readiness(session.context)
    return GuidedIntakeReadiness(
        context_id=session.context.id,
        session_complete=(
            session.state.value == "complete"
            and run.state is GuidedIntakeRunState.COMPLETE
        ),
        human_intake_complete=intake.complete and intake.warning_count == 0,
        remaining_question_count=len(list_questions(session.context)),
        provider_turn_count=len(run.turns),
        live_provider_used=run.live_provider_used,
        full_adaptation_blocker_count=full.blocker_count,
    )
