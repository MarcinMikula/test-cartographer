"""State transitions for persisted deterministic intake sessions."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.context.models import ContextBundle
from test_cartographer.intake.answers import apply_answer
from test_cartographer.intake.enums import IntakeAnswerAction, IntakeSessionState
from test_cartographer.intake.models import (
    IntakeAnswer,
    IntakeInteraction,
    IntakeQuestion,
    IntakeSession,
)
from test_cartographer.intake.rules import assess_intake, select_next_question


def create_session(
    context: ContextBundle,
    *,
    session_id: str,
    started_at: datetime,
) -> IntakeSession:
    """Create and immediately classify one intake session."""

    session = IntakeSession(
        id=session_id,
        state=IntakeSessionState.ACTIVE,
        started_at=started_at,
        updated_at=started_at,
        context=context,
    )
    return refresh_session_state(session, updated_at=started_at)


def record_answer(
    session: IntakeSession,
    *,
    question: IntakeQuestion,
    answer: IntakeAnswer,
    asked_at: datetime,
    answered_at: datetime,
    active_seconds: float,
) -> IntakeSession:
    """Apply one answer, record effort, and deterministically refresh state."""

    expected = select_next_question(
        session.context,
        excluded_question_ids=session.deferred_question_ids,
    )
    if expected is None or expected != question:
        raise ValueError("question is not the current deterministic intake question")

    updated_context = apply_answer(
        session.context,
        session_id=session.id,
        question=question,
        answer=answer,
        answered_at=answered_at,
    )
    deferred = list(session.deferred_question_ids)
    if answer.action in {IntakeAnswerAction.UNKNOWN, IntakeAnswerAction.SKIP}:
        if question.id not in deferred:
            deferred.append(question.id)
    else:
        deferred = [item for item in deferred if item != question.id]

    interaction = IntakeInteraction(
        sequence=len(session.interactions) + 1,
        question_id=question.id,
        question_kind=question.kind,
        prompt=question.prompt,
        target_path=question.target_path,
        action=answer.action,
        asked_at=asked_at,
        answered_at=answered_at,
        active_seconds=active_seconds,
    )
    updated = session.model_copy(
        update={
            "state": IntakeSessionState.ACTIVE,
            "updated_at": answered_at,
            "context": updated_context,
            "interactions": (*session.interactions, interaction),
            "deferred_question_ids": tuple(deferred),
        }
    )
    validated = IntakeSession.model_validate(updated.model_dump(mode="python"))
    return refresh_session_state(validated, updated_at=answered_at)


def pause_session(session: IntakeSession, *, updated_at: datetime) -> IntakeSession:
    updated = session.model_copy(
        update={"state": IntakeSessionState.PAUSED, "updated_at": updated_at}
    )
    return IntakeSession.model_validate(updated.model_dump(mode="python"))


def resume_session(
    session: IntakeSession,
    *,
    updated_at: datetime,
    retry_deferred: bool = False,
) -> IntakeSession:
    deferred = () if retry_deferred else session.deferred_question_ids
    updated = session.model_copy(
        update={
            "state": IntakeSessionState.ACTIVE,
            "updated_at": updated_at,
            "deferred_question_ids": deferred,
        }
    )
    validated = IntakeSession.model_validate(updated.model_dump(mode="python"))
    return refresh_session_state(validated, updated_at=updated_at)


def refresh_session_state(
    session: IntakeSession,
    *,
    updated_at: datetime,
) -> IntakeSession:
    """Classify a session without changing its context or interaction history."""

    next_question = select_next_question(
        session.context,
        excluded_question_ids=session.deferred_question_ids,
    )
    if next_question is not None:
        state = IntakeSessionState.ACTIVE
    elif assess_intake(session.context).complete:
        state = IntakeSessionState.COMPLETE
    else:
        state = IntakeSessionState.BLOCKED

    updated = session.model_copy(update={"state": state, "updated_at": updated_at})
    return IntakeSession.model_validate(updated.model_dump(mode="python"))
