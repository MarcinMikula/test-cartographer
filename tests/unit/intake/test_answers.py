from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.context.io import load_context
from test_cartographer.intake.answers import apply_answer
from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.rules import list_questions

ROOT = Path(__file__).resolve().parents[3]
ANSWERED_AT = datetime(2026, 8, 1, 13, 0, tzinfo=timezone.utc)


def _context(state: str):
    return load_context(ROOT / "testdata" / "context" / state / "public_search_flow.json")


def _question(context, question_id: str):
    return next(item for item in list_questions(context) if item.id == question_id)


def test_provided_risk_updates_context_and_appends_human_evidence() -> None:
    context = _context("incomplete")
    question = _question(context, "q_process_risk")

    updated = apply_answer(
        context,
        session_id="intake_reference",
        question=question,
        answer=IntakeAnswer(
            action=IntakeAnswerAction.PROVIDE,
            value="Search failures can hide relevant catalog items from users.",
        ),
        answered_at=ANSWERED_AT,
    )

    assert context.process.risk.status is KnowledgeStatus.UNKNOWN
    assert updated.process.risk.status is KnowledgeStatus.PROVIDED
    assert updated.process.risk.value.startswith("Search failures")
    assert updated.process.risk.evidence_ids == ("ev_intake_001",)
    assert updated.evidence[-1].source_ref == "intake:intake_reference:q_process_risk"
    assert updated.updated_at == ANSWERED_AT


def test_provided_expected_outcome_updates_selected_outcome_only() -> None:
    context = _context("incomplete")
    question = _question(context, "q_outcome_outcome_matching_results")

    updated = apply_answer(
        context,
        session_id="intake_reference",
        question=question,
        answer=IntakeAnswer(
            action=IntakeAnswerAction.PROVIDE,
            value="The visible result list contains items matching the query.",
        ),
        answered_at=ANSWERED_AT,
    )

    outcome = updated.process.expected_outcomes[0]
    assert outcome.statement.status is KnowledgeStatus.PROVIDED
    assert outcome.statement.value == (
        "The visible result list contains items matching the query."
    )


def test_unknown_action_preserves_explicit_unknown_without_evidence() -> None:
    context = _context("incomplete")
    question = _question(context, "q_process_risk")

    updated = apply_answer(
        context,
        session_id="intake_reference",
        question=question,
        answer=IntakeAnswer(action=IntakeAnswerAction.UNKNOWN),
        answered_at=ANSWERED_AT,
    )

    assert updated.process.risk.status is KnowledgeStatus.UNKNOWN
    assert updated.process.risk.value is None
    assert updated.process.risk.evidence_ids == ()
    assert "explicitly marked" in (updated.process.risk.notes or "")
    assert len(updated.evidence) == len(context.evidence)


def test_skip_does_not_modify_context() -> None:
    context = _context("incomplete")
    question = _question(context, "q_process_risk")

    updated = apply_answer(
        context,
        session_id="intake_reference",
        question=question,
        answer=IntakeAnswer(action=IntakeAnswerAction.SKIP),
        answered_at=ANSWERED_AT,
    )

    assert updated is context


def test_open_question_answer_is_retained_as_evidence_and_question_is_removed() -> None:
    context = _context("incomplete")
    question = _question(context, "q_open_question_expected_matching_rule")

    updated = apply_answer(
        context,
        session_id="intake_reference",
        question=question,
        answer=IntakeAnswer(
            action=IntakeAnswerAction.PROVIDE,
            value="An item matches when its title contains the query case-insensitively.",
        ),
        answered_at=ANSWERED_AT,
    )

    assert updated.open_questions == ()
    assert "case-insensitively" in updated.evidence[-1].summary
    assert updated.evidence[-1].content_sha256 is not None


def test_disallowed_confirmation_is_rejected() -> None:
    context = _context("incomplete")
    question = _question(context, "q_process_risk")

    with pytest.raises(ValueError, match="not allowed"):
        apply_answer(
            context,
            session_id="intake_reference",
            question=question,
            answer=IntakeAnswer(action=IntakeAnswerAction.CONFIRM),
            answered_at=ANSWERED_AT,
        )


def test_conflict_resolution_is_stored_as_provided_knowledge() -> None:
    context = _context("conflicting")
    question = list_questions(context)[0]

    updated = apply_answer(
        context,
        session_id="intake_reference",
        question=question,
        answer=IntakeAnswer(
            action=IntakeAnswerAction.PROVIDE,
            value="Use the tester-confirmed matching rule for this reference flow.",
        ),
        answered_at=ANSWERED_AT,
    )

    assert updated.conflicts[0].resolution.status is KnowledgeStatus.PROVIDED
    assert updated.conflicts[0].resolution.evidence_ids == ("ev_intake_001",)
