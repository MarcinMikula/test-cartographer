from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.io import load_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.intake.enums import IntakeAnswerAction, IntakeSessionState
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.rules import assess_intake, select_next_question
from test_cartographer.intake.session import (
    create_session,
    pause_session,
    record_answer,
    resume_session,
)

ROOT = Path(__file__).resolve().parents[3]
START = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _context(state: str = "incomplete"):
    return load_context(ROOT / "testdata" / "context" / state / "public_search_flow.json")


def _respond(
    session,
    action: IntakeAnswerAction,
    value: str | None = None,
    seconds: float = 1.0,
):
    question = select_next_question(
        session.context,
        excluded_question_ids=session.deferred_question_ids,
    )
    assert question is not None
    asked_at = session.updated_at + timedelta(seconds=1)
    answered_at = asked_at + timedelta(seconds=seconds)
    return record_answer(
        session,
        question=question,
        answer=IntakeAnswer(action=action, value=value),
        asked_at=asked_at,
        answered_at=answered_at,
        active_seconds=seconds,
    )


def _provide(session, value: str, seconds: float = 1.0):
    return _respond(session, IntakeAnswerAction.PROVIDE, value, seconds)


def _confirm(session, seconds: float = 1.0):
    return _respond(session, IntakeAnswerAction.CONFIRM, None, seconds)


def test_create_session_selects_first_deterministic_question() -> None:
    session = create_session(
        _context(),
        session_id="intake_reference",
        started_at=START,
    )

    question = select_next_question(session.context)

    assert session.state is IntakeSessionState.ACTIVE
    assert question is not None
    assert question.id == "q_process_risk"


def test_collection_and_review_complete_human_intake_but_not_full_adaptation() -> None:
    session = create_session(
        _context(),
        session_id="intake_reference",
        started_at=START,
    )
    session = _provide(session, "Search failures can hide relevant items.", 1.0)
    session = _provide(session, "Matching items are visible in the result list.", 1.0)
    session = _provide(session, "A title contains the query case-insensitively.", 1.0)

    assert select_next_question(session.context).id == "q_process_risk"

    session = _confirm(session, 1.0)
    session = _confirm(session, 1.0)

    assert session.state is IntakeSessionState.COMPLETE
    assert assess_intake(session.context).complete is True
    assert assess_intake(session.context).warning_count == 0
    assert assess_readiness(session.context).ready is False
    assert session.metrics.interaction_count == 5
    assert session.metrics.provided_count == 3
    assert session.metrics.confirmed_count == 2
    assert session.metrics.active_seconds == 5.0


def test_unknown_answer_is_deferred_and_session_can_become_blocked() -> None:
    session = create_session(
        _context(),
        session_id="intake_reference",
        started_at=START,
    )
    session = _respond(session, IntakeAnswerAction.UNKNOWN)
    session = _provide(session, "Matching items are visible.")
    session = _provide(session, "A title contains the query.")

    assert session.state is IntakeSessionState.BLOCKED
    assert session.deferred_question_ids == ("q_process_risk",)
    assert session.metrics.unknown_count == 1


def test_retry_deferred_reopens_unknown_question() -> None:
    session = create_session(
        _context(),
        session_id="intake_reference",
        started_at=START,
    )
    session = _respond(session, IntakeAnswerAction.UNKNOWN)

    resumed = resume_session(
        session,
        updated_at=START + timedelta(minutes=1),
        retry_deferred=True,
    )

    assert resumed.deferred_question_ids == ()
    assert select_next_question(resumed.context).id == "q_process_risk"


def test_pause_and_resume_preserve_context_and_history() -> None:
    session = create_session(
        _context(),
        session_id="intake_reference",
        started_at=START,
    )
    session = _provide(session, "Search failures can hide relevant items.")
    paused = pause_session(session, updated_at=START + timedelta(minutes=2))
    resumed = resume_session(paused, updated_at=START + timedelta(minutes=3))

    assert paused.state is IntakeSessionState.PAUSED
    assert resumed.state is IntakeSessionState.ACTIVE
    assert resumed.context == session.context
    assert resumed.interactions == session.interactions

def test_record_answer_persists_actual_operator_facing_prompt() -> None:
    session = create_session(
        _context(),
        session_id="intake_operator_prompt",
        started_at=START,
    )
    question = select_next_question(session.context)
    assert question is not None
    asked_at = START + timedelta(seconds=1)

    updated = record_answer(
        session,
        question=question,
        answer=IntakeAnswer(
            action=IntakeAnswerAction.PROVIDE,
            value="Search failures can hide relevant products.",
        ),
        asked_at=asked_at,
        answered_at=asked_at + timedelta(seconds=1),
        active_seconds=1.0,
        interaction_prompt="Which material search failure should this test protect against?",
    )

    assert (
        updated.interactions[-1].prompt
        == "Which material search failure should this test protect against?"
    )
