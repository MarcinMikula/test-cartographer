"""Apply validated human answers to immutable context bundles."""

from __future__ import annotations

import hashlib
from datetime import datetime

from test_cartographer.context.enums import EvidenceSourceType, KnowledgeStatus
from test_cartographer.context.models import (
    Conflict,
    ContextBundle,
    Evidence,
    ExpectedOutcome,
    KnowledgeText,
    ProcessContext,
)
from test_cartographer.intake.enums import IntakeAnswerAction, IntakeQuestionKind
from test_cartographer.intake.models import IntakeAnswer, IntakeQuestion


def apply_answer(
    context: ContextBundle,
    *,
    session_id: str,
    question: IntakeQuestion,
    answer: IntakeAnswer,
    answered_at: datetime,
) -> ContextBundle:
    """Return a revalidated context updated by one allowed intake answer."""

    if answer.action not in question.allowed_actions:
        raise ValueError(
            f"action {answer.action.value} is not allowed for {question.id}"
        )
    if answered_at.tzinfo is None or answered_at.utcoffset() is None:
        raise ValueError("answered_at must include a timezone offset")
    if answer.action is IntakeAnswerAction.SKIP:
        return context

    if question.kind is IntakeQuestionKind.OPEN_QUESTION:
        return _apply_open_question_answer(
            context,
            session_id=session_id,
            question=question,
            answer=answer,
            answered_at=answered_at,
        )

    if answer.action is IntakeAnswerAction.UNKNOWN:
        replacement = KnowledgeText(
            value=None,
            status=KnowledgeStatus.UNKNOWN,
            evidence_ids=(),
            confidence=None,
            sensitivity=question.sensitivity,
            notes="User explicitly marked this information as unknown during intake.",
        )
        return _replace_knowledge(context, question, replacement, answered_at)

    current = _current_knowledge(context, question)
    value = answer.value if answer.action is IntakeAnswerAction.PROVIDE else current.value
    if value is None:
        raise ValueError("confirm action requires an existing value")

    evidence = _human_evidence(
        context,
        session_id=session_id,
        question=question,
        answer_value=value,
        answered_at=answered_at,
        include_value=False,
    )
    status = (
        KnowledgeStatus.PROVIDED
        if answer.action is IntakeAnswerAction.PROVIDE
        else KnowledgeStatus.CONFIRMED
    )
    evidence_ids = (
        (evidence.id,)
        if answer.action is IntakeAnswerAction.PROVIDE
        else tuple(dict.fromkeys((*current.evidence_ids, evidence.id)))
    )
    replacement = KnowledgeText(
        value=value,
        status=status,
        evidence_ids=evidence_ids,
        confidence=None,
        sensitivity=current.sensitivity,
        notes=current.notes,
    )
    return _replace_knowledge(
        context,
        question,
        replacement,
        answered_at,
        evidence=evidence,
    )


def _apply_open_question_answer(
    context: ContextBundle,
    *,
    session_id: str,
    question: IntakeQuestion,
    answer: IntakeAnswer,
    answered_at: datetime,
) -> ContextBundle:
    if answer.action in {IntakeAnswerAction.UNKNOWN, IntakeAnswerAction.SKIP}:
        return context
    if answer.action is IntakeAnswerAction.CONFIRM:
        raise ValueError("an open question has no existing value to confirm")
    if answer.value is None:
        raise ValueError("open-question answer requires a value")

    evidence = _human_evidence(
        context,
        session_id=session_id,
        question=question,
        answer_value=answer.value,
        answered_at=answered_at,
        include_value=True,
    )
    updated = context.model_copy(
        update={
            "updated_at": answered_at,
            "open_questions": tuple(
                item for item in context.open_questions if item.id != question.subject_id
            ),
            "evidence": (*context.evidence, evidence),
        }
    )
    return ContextBundle.model_validate(updated.model_dump(mode="python"))


def _current_knowledge(
    context: ContextBundle,
    question: IntakeQuestion,
) -> KnowledgeText:
    process = context.process
    if question.kind is IntakeQuestionKind.PROCESS_PURPOSE:
        return process.purpose
    if question.kind is IntakeQuestionKind.PROCESS_RISK:
        return process.risk
    if question.kind is IntakeQuestionKind.PROCESS_ROLE:
        return process.role
    if question.kind is IntakeQuestionKind.PRECONDITION:
        index = _precondition_index(question.target_path)
        return process.preconditions[index]
    if question.kind is IntakeQuestionKind.EXPECTED_OUTCOME:
        return next(
            outcome.statement
            for outcome in process.expected_outcomes
            if outcome.id == question.subject_id
        )
    if question.kind is IntakeQuestionKind.CONFLICT_RESOLUTION:
        return next(
            conflict.resolution
            for conflict in context.conflicts
            if conflict.id == question.subject_id
        )
    raise ValueError(f"question kind {question.kind.value} has no KnowledgeText target")


def _replace_knowledge(
    context: ContextBundle,
    question: IntakeQuestion,
    replacement: KnowledgeText,
    updated_at: datetime,
    *,
    evidence: Evidence | None = None,
) -> ContextBundle:
    process = context.process
    conflicts = context.conflicts

    if question.kind is IntakeQuestionKind.PROCESS_PURPOSE:
        process = process.model_copy(update={"purpose": replacement})
    elif question.kind is IntakeQuestionKind.PROCESS_RISK:
        process = process.model_copy(update={"risk": replacement})
    elif question.kind is IntakeQuestionKind.PROCESS_ROLE:
        process = process.model_copy(update={"role": replacement})
    elif question.kind is IntakeQuestionKind.PRECONDITION:
        index = _precondition_index(question.target_path)
        preconditions = list(process.preconditions)
        preconditions[index] = replacement
        process = process.model_copy(update={"preconditions": tuple(preconditions)})
    elif question.kind is IntakeQuestionKind.EXPECTED_OUTCOME:
        outcomes = tuple(
            ExpectedOutcome(
                id=outcome.id,
                statement=(replacement if outcome.id == question.subject_id else outcome.statement),
                related_element_ids=outcome.related_element_ids,
            )
            for outcome in process.expected_outcomes
        )
        process = process.model_copy(update={"expected_outcomes": outcomes})
    elif question.kind is IntakeQuestionKind.CONFLICT_RESOLUTION:
        conflicts = tuple(
            Conflict(
                id=conflict.id,
                subject_id=conflict.subject_id,
                description=conflict.description,
                evidence_ids=conflict.evidence_ids,
                resolution=(replacement if conflict.id == question.subject_id else conflict.resolution),
            )
            for conflict in context.conflicts
        )
    else:
        raise ValueError(f"unsupported knowledge target {question.kind.value}")

    updated = context.model_copy(
        update={
            "process": ProcessContext.model_validate(process.model_dump(mode="python")),
            "conflicts": conflicts,
            "updated_at": updated_at,
            "evidence": (
                (*context.evidence, evidence)
                if evidence is not None
                else context.evidence
            ),
        }
    )
    return ContextBundle.model_validate(updated.model_dump(mode="python"))


def _human_evidence(
    context: ContextBundle,
    *,
    session_id: str,
    question: IntakeQuestion,
    answer_value: str,
    answered_at: datetime,
    include_value: bool,
) -> Evidence:
    evidence_id = _next_evidence_id(context)
    summary = f"Human intake answer for {question.target_path}."
    if include_value:
        summary = f"Human answer to {question.prompt!r}: {answer_value}"
    return Evidence(
        id=evidence_id,
        source_type=EvidenceSourceType.HUMAN,
        source_ref=f"intake:{session_id}:{question.id}",
        summary=summary,
        captured_at=answered_at,
        sensitivity=question.sensitivity,
        content_sha256=hashlib.sha256(answer_value.encode("utf-8")).hexdigest(),
    )


def _next_evidence_id(context: ContextBundle) -> str:
    existing = {item.id for item in context.evidence}
    counter = 1
    while True:
        candidate = f"ev_intake_{counter:03d}"
        if candidate not in existing:
            return candidate
        counter += 1


def _precondition_index(target_path: str) -> int:
    prefix = "process.preconditions["
    if not target_path.startswith(prefix) or not target_path.endswith("]"):
        raise ValueError(f"invalid precondition target path: {target_path}")
    return int(target_path[len(prefix) : -1])
