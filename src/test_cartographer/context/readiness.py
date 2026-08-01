"""Deterministic assessment of whether a valid context is ready for adaptation."""

from __future__ import annotations

from pydantic import Field, computed_field

from test_cartographer.context.enums import (
    ActionKind,
    KnowledgeStatus,
    ReadinessSeverity,
)
from test_cartographer.context.models import (
    ContextBundle,
    ContractModel,
    Identifier,
    KnowledgeText,
)


class ReadinessIssue(ContractModel):
    code: Identifier
    severity: ReadinessSeverity
    path: str = Field(min_length=1)
    message: str = Field(min_length=1)
    related_ids: tuple[Identifier, ...] = ()


class ContextReadinessReport(ContractModel):
    context_id: Identifier
    issues: tuple[ReadinessIssue, ...] = ()

    @computed_field
    @property
    def ready(self) -> bool:
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


def assess_readiness(context: ContextBundle) -> ContextReadinessReport:
    """Assess one structurally valid context without mutating or completing it."""

    issues: list[ReadinessIssue] = []

    _check_business_value(
        issues,
        context.process.purpose,
        path="process.purpose",
        code="purpose_not_confirmed",
        related_id=context.process.id,
    )
    _check_business_value(
        issues,
        context.process.risk,
        path="process.risk",
        code="risk_not_confirmed",
        related_id=context.process.id,
    )
    _check_business_value(
        issues,
        context.process.role,
        path="process.role",
        code="role_not_confirmed",
        related_id=context.process.id,
    )

    for index, precondition in enumerate(context.process.preconditions):
        _check_business_value(
            issues,
            precondition,
            path=f"process.preconditions[{index}]",
            code="precondition_not_confirmed",
            related_id=context.process.id,
        )

    for outcome in context.process.expected_outcomes:
        _check_business_value(
            issues,
            outcome.statement,
            path=f"process.expected_outcomes.{outcome.id}.statement",
            code="outcome_not_confirmed",
            related_id=outcome.id,
        )

    element_by_id = {element.id: element for element in context.elements}
    for step in context.process.steps:
        _check_usable_value(
            issues,
            step.intent,
            path=f"process.steps.{step.id}.intent",
            code="step_intent_unusable",
            related_id=step.id,
        )
        _check_usable_value(
            issues,
            step.expected_state,
            path=f"process.steps.{step.id}.expected_state",
            code="step_state_unusable",
            related_id=step.id,
        )

        if step.action.kind is ActionKind.NAVIGATE:
            continue

        target_id = step.action.target_element_id
        if target_id is None:
            continue
        element = element_by_id[target_id]
        primary = [
            candidate for candidate in element.locator_candidates if candidate.primary
        ]
        if not primary:
            issues.append(
                ReadinessIssue(
                    code="primary_locator_missing",
                    severity=ReadinessSeverity.BLOCKER,
                    path=f"elements.{element.id}.locator_candidates",
                    message="An action target requires one selected primary locator.",
                    related_ids=(element.id,),
                )
            )
            continue

        locator = primary[0]
        if locator.value.status not in {
            KnowledgeStatus.OBSERVED,
            KnowledgeStatus.CONFIRMED,
        }:
            issues.append(
                ReadinessIssue(
                    code="primary_locator_not_observed",
                    severity=ReadinessSeverity.BLOCKER,
                    path=f"elements.{element.id}.locators.{locator.id}.value",
                    message=(
                        "A primary locator must be observed in the application or "
                        "explicitly confirmed before framework adaptation."
                    ),
                    related_ids=(element.id, locator.id),
                )
            )

    for conflict in context.conflicts:
        if conflict.resolution.status is KnowledgeStatus.UNKNOWN:
            issues.append(
                ReadinessIssue(
                    code="conflict_unresolved",
                    severity=ReadinessSeverity.BLOCKER,
                    path=f"conflicts.{conflict.id}.resolution",
                    message="A recorded conflict must be resolved before adaptation.",
                    related_ids=(conflict.id, conflict.subject_id),
                )
            )

    for question in context.open_questions:
        issues.append(
            ReadinessIssue(
                code=(
                    "blocking_question_open"
                    if question.blocking
                    else "nonblocking_question_open"
                ),
                severity=(
                    ReadinessSeverity.BLOCKER
                    if question.blocking
                    else ReadinessSeverity.WARNING
                ),
                path=f"open_questions.{question.id}",
                message=question.question,
                related_ids=(question.id, *question.related_ids),
            )
        )

    return ContextReadinessReport(
        context_id=context.id,
        issues=tuple(issues),
    )


def _check_business_value(
    issues: list[ReadinessIssue],
    value: KnowledgeText,
    *,
    path: str,
    code: str,
    related_id: str,
) -> None:
    if value.status is KnowledgeStatus.CONFIRMED:
        return

    if value.status in {KnowledgeStatus.OBSERVED, KnowledgeStatus.PROVIDED}:
        issues.append(
            ReadinessIssue(
                code=code,
                severity=ReadinessSeverity.WARNING,
                path=path,
                message="Business-critical context is supported but not yet confirmed.",
                related_ids=(related_id,),
            )
        )
        return

    issues.append(
        ReadinessIssue(
            code=code,
            severity=ReadinessSeverity.BLOCKER,
            path=path,
            message=(
                "Business-critical context is unknown, inferred, stale, or "
                "conflicting and requires human confirmation."
            ),
            related_ids=(related_id,),
        )
    )


def _check_usable_value(
    issues: list[ReadinessIssue],
    value: KnowledgeText,
    *,
    path: str,
    code: str,
    related_id: str,
) -> None:
    if value.status in {
        KnowledgeStatus.OBSERVED,
        KnowledgeStatus.PROVIDED,
        KnowledgeStatus.CONFIRMED,
    }:
        return

    severity = (
        ReadinessSeverity.WARNING
        if value.status is KnowledgeStatus.INFERRED
        else ReadinessSeverity.BLOCKER
    )
    issues.append(
        ReadinessIssue(
            code=code,
            severity=severity,
            path=path,
            message="The value is not yet supported by current usable context.",
            related_ids=(related_id,),
        )
    )
