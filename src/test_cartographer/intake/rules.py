"""Deterministic intake assessment and question-selection rules."""

from __future__ import annotations

import hashlib

from pydantic import computed_field

from test_cartographer.context.enums import KnowledgeStatus, ReadinessSeverity
from test_cartographer.context.models import (
    ContextBundle,
    ContractModel,
    Identifier,
    KnowledgeText,
)
from test_cartographer.context.readiness import ReadinessIssue, assess_readiness
from test_cartographer.intake.enums import (
    IntakeAnswerAction,
    IntakeQuestionKind,
)
from test_cartographer.intake.models import IntakeQuestion

_HUMAN_INTAKE_CODES = frozenset(
    {
        "purpose_not_confirmed",
        "risk_not_confirmed",
        "role_not_confirmed",
        "precondition_not_confirmed",
        "outcome_not_confirmed",
        "conflict_unresolved",
        "blocking_question_open",
        "nonblocking_question_open",
    }
)


class IntakeAssessment(ContractModel):
    """Human-answerable subset of the full adaptation-readiness report."""

    context_id: Identifier
    issues: tuple[ReadinessIssue, ...] = ()

    @computed_field
    @property
    def complete(self) -> bool:
        return not any(
            issue.severity is ReadinessSeverity.BLOCKER for issue in self.issues
        )

    @computed_field
    @property
    def blocker_count(self) -> int:
        return sum(
            issue.severity is ReadinessSeverity.BLOCKER for issue in self.issues
        )

    @computed_field
    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity is ReadinessSeverity.WARNING for issue in self.issues
        )


def assess_intake(context: ContextBundle) -> IntakeAssessment:
    """Return only issues that deterministic human intake can address."""

    full_report = assess_readiness(context)
    return IntakeAssessment(
        context_id=context.id,
        issues=tuple(
            issue for issue in full_report.issues if issue.code in _HUMAN_INTAKE_CODES
        ),
    )


def list_questions(context: ContextBundle) -> tuple[IntakeQuestion, ...]:
    """Build the ordered collection and review queue for current context."""

    required: list[IntakeQuestion] = []

    for conflict in context.conflicts:
        if _requires_human_input(conflict.resolution):
            required.append(
                IntakeQuestion(
                    id=_question_id("conflict", conflict.id),
                    kind=IntakeQuestionKind.CONFLICT_RESOLUTION,
                    prompt=(
                        "How should this conflict be resolved? "
                        f"{conflict.description}"
                    ),
                    target_path=f"conflicts.{conflict.id}.resolution",
                    subject_id=conflict.id,
                    current_value=conflict.resolution.value,
                    sensitivity=conflict.resolution.sensitivity,
                    allowed_actions=_allowed_actions(conflict.resolution),
                )
            )

    _append_required_question(
        required,
        value=context.process.purpose,
        question_id="q_process_purpose",
        kind=IntakeQuestionKind.PROCESS_PURPOSE,
        prompt="What business outcome should this process achieve?",
        target_path="process.purpose",
        subject_id=context.process.id,
    )
    _append_required_question(
        required,
        value=context.process.risk,
        question_id="q_process_risk",
        kind=IntakeQuestionKind.PROCESS_RISK,
        prompt="What failure or business risk should this test protect against?",
        target_path="process.risk",
        subject_id=context.process.id,
    )
    _append_required_question(
        required,
        value=context.process.role,
        question_id="q_process_role",
        kind=IntakeQuestionKind.PROCESS_ROLE,
        prompt="Which user role performs this process?",
        target_path="process.role",
        subject_id=context.process.id,
    )

    for index, precondition in enumerate(context.process.preconditions):
        _append_required_question(
            required,
            value=precondition,
            question_id=_question_id("precondition", str(index + 1)),
            kind=IntakeQuestionKind.PRECONDITION,
            prompt=f"What must be true for precondition {index + 1}?",
            target_path=f"process.preconditions[{index}]",
            subject_id=context.process.id,
        )

    for outcome in context.process.expected_outcomes:
        _append_required_question(
            required,
            value=outcome.statement,
            question_id=_question_id("outcome", outcome.id),
            kind=IntakeQuestionKind.EXPECTED_OUTCOME,
            prompt="What observable result proves that this outcome succeeded?",
            target_path=f"process.expected_outcomes.{outcome.id}.statement",
            subject_id=outcome.id,
        )

    for question in context.open_questions:
        required.append(
            IntakeQuestion(
                id=_question_id("open", question.id),
                kind=IntakeQuestionKind.OPEN_QUESTION,
                prompt=question.question,
                target_path=f"open_questions.{question.id}",
                subject_id=question.id,
                current_value=None,
                allowed_actions=(
                    IntakeAnswerAction.PROVIDE,
                    IntakeAnswerAction.UNKNOWN,
                    IntakeAnswerAction.SKIP,
                ),
            )
        )

    if required:
        return tuple(required)

    review: list[IntakeQuestion] = []
    for conflict in context.conflicts:
        _append_review_question(
            review,
            value=conflict.resolution,
            question_id=_question_id("conflict", conflict.id),
            kind=IntakeQuestionKind.CONFLICT_RESOLUTION,
            prompt="Review and confirm the proposed conflict resolution.",
            target_path=f"conflicts.{conflict.id}.resolution",
            subject_id=conflict.id,
        )

    _append_review_question(
        review,
        value=context.process.purpose,
        question_id="q_process_purpose",
        kind=IntakeQuestionKind.PROCESS_PURPOSE,
        prompt="Review and confirm the process purpose.",
        target_path="process.purpose",
        subject_id=context.process.id,
    )
    _append_review_question(
        review,
        value=context.process.risk,
        question_id="q_process_risk",
        kind=IntakeQuestionKind.PROCESS_RISK,
        prompt="Review and confirm the business risk.",
        target_path="process.risk",
        subject_id=context.process.id,
    )
    _append_review_question(
        review,
        value=context.process.role,
        question_id="q_process_role",
        kind=IntakeQuestionKind.PROCESS_ROLE,
        prompt="Review and confirm the user role.",
        target_path="process.role",
        subject_id=context.process.id,
    )

    for index, precondition in enumerate(context.process.preconditions):
        _append_review_question(
            review,
            value=precondition,
            question_id=_question_id("precondition", str(index + 1)),
            kind=IntakeQuestionKind.PRECONDITION,
            prompt=f"Review and confirm precondition {index + 1}.",
            target_path=f"process.preconditions[{index}]",
            subject_id=context.process.id,
        )

    for outcome in context.process.expected_outcomes:
        _append_review_question(
            review,
            value=outcome.statement,
            question_id=_question_id("outcome", outcome.id),
            kind=IntakeQuestionKind.EXPECTED_OUTCOME,
            prompt="Review and confirm the expected outcome.",
            target_path=f"process.expected_outcomes.{outcome.id}.statement",
            subject_id=outcome.id,
        )

    return tuple(review)


def select_next_question(
    context: ContextBundle,
    *,
    excluded_question_ids: tuple[str, ...] = (),
) -> IntakeQuestion | None:
    """Select the first current question not deferred by the active session."""

    excluded = set(excluded_question_ids)
    return next(
        (question for question in list_questions(context) if question.id not in excluded),
        None,
    )


def _append_required_question(
    questions: list[IntakeQuestion],
    *,
    value: KnowledgeText,
    question_id: str,
    kind: IntakeQuestionKind,
    prompt: str,
    target_path: str,
    subject_id: str,
) -> None:
    if not _requires_human_input(value):
        return
    questions.append(
        IntakeQuestion(
            id=question_id,
            kind=kind,
            prompt=prompt,
            target_path=target_path,
            subject_id=subject_id,
            current_value=value.value,
            sensitivity=value.sensitivity,
            allowed_actions=_allowed_actions(value),
        )
    )


def _append_review_question(
    questions: list[IntakeQuestion],
    *,
    value: KnowledgeText,
    question_id: str,
    kind: IntakeQuestionKind,
    prompt: str,
    target_path: str,
    subject_id: str,
) -> None:
    if value.status not in {KnowledgeStatus.PROVIDED, KnowledgeStatus.OBSERVED}:
        return
    questions.append(
        IntakeQuestion(
            id=question_id,
            kind=kind,
            prompt=prompt,
            target_path=target_path,
            subject_id=subject_id,
            current_value=value.value,
            sensitivity=value.sensitivity,
            allowed_actions=(
                IntakeAnswerAction.CONFIRM,
                IntakeAnswerAction.PROVIDE,
                IntakeAnswerAction.UNKNOWN,
                IntakeAnswerAction.SKIP,
            ),
        )
    )


def _requires_human_input(value: KnowledgeText) -> bool:
    return value.status in {
        KnowledgeStatus.UNKNOWN,
        KnowledgeStatus.INFERRED,
        KnowledgeStatus.STALE,
        KnowledgeStatus.CONFLICTING,
    }


def _allowed_actions(value: KnowledgeText) -> tuple[IntakeAnswerAction, ...]:
    actions = [IntakeAnswerAction.PROVIDE]
    if value.value is not None:
        actions.append(IntakeAnswerAction.CONFIRM)
    actions.extend((IntakeAnswerAction.UNKNOWN, IntakeAnswerAction.SKIP))
    return tuple(actions)


def _question_id(prefix: str, subject: str) -> str:
    raw = f"q_{prefix}_{subject}"
    if len(raw) <= 64:
        return raw
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
    return f"{raw[:55]}_{digest}"
