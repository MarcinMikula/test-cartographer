"""Strict models for deterministic human-guided intake sessions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.models import (
    ContextBundle,
    ContractModel,
    Identifier,
    NonEmptyText,
)
from test_cartographer.intake.enums import (
    IntakeAnswerAction,
    IntakeQuestionKind,
    IntakeSessionState,
)


class IntakeQuestion(ContractModel):
    """One deterministic question selected from current context state."""

    id: Identifier
    kind: IntakeQuestionKind
    prompt: NonEmptyText
    target_path: NonEmptyText
    subject_id: Identifier
    current_value: NonEmptyText | None = None
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    allowed_actions: tuple[IntakeAnswerAction, ...] = Field(min_length=1)

    @field_validator("allowed_actions")
    @classmethod
    def actions_must_be_unique(
        cls,
        value: tuple[IntakeAnswerAction, ...],
    ) -> tuple[IntakeAnswerAction, ...]:
        if len(value) != len(set(value)):
            raise ValueError("allowed_actions must be unique")
        return value


class IntakeAnswer(ContractModel):
    """One validated user response to an intake question."""

    action: IntakeAnswerAction
    value: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_action_value(self) -> IntakeAnswer:
        if self.action is IntakeAnswerAction.PROVIDE and self.value is None:
            raise ValueError("provide action requires a value")
        if self.action is not IntakeAnswerAction.PROVIDE and self.value is not None:
            raise ValueError(f"{self.action.value} action must not contain a value")
        return self


class IntakeInteraction(ContractModel):
    """Audit and effort record for one answered or deferred question."""

    sequence: int = Field(ge=1)
    question_id: Identifier
    question_kind: IntakeQuestionKind
    prompt: NonEmptyText
    target_path: NonEmptyText
    action: IntakeAnswerAction
    asked_at: datetime
    answered_at: datetime
    active_seconds: float = Field(ge=0.0)

    @field_validator("asked_at", "answered_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("interaction timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def answered_at_must_not_precede_asked_at(self) -> IntakeInteraction:
        if self.answered_at < self.asked_at:
            raise ValueError("answered_at must not be earlier than asked_at")
        return self


class IntakeMetrics(ContractModel):
    """Deterministic summary of operator effort recorded by one session."""

    interaction_count: int = Field(ge=0)
    provided_count: int = Field(ge=0)
    confirmed_count: int = Field(ge=0)
    unknown_count: int = Field(ge=0)
    skipped_count: int = Field(ge=0)
    active_seconds: float = Field(ge=0.0)


class IntakeSession(ContractModel):
    """Self-contained persisted state for one human-guided intake run."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    state: IntakeSessionState
    started_at: datetime
    updated_at: datetime
    context: ContextBundle
    interactions: tuple[IntakeInteraction, ...] = ()
    deferred_question_ids: tuple[Identifier, ...] = ()

    @field_validator("started_at", "updated_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("session timestamps must include a timezone offset")
        return value

    @field_validator("deferred_question_ids")
    @classmethod
    def deferred_ids_must_be_unique(
        cls,
        value: tuple[Identifier, ...],
    ) -> tuple[Identifier, ...]:
        if len(value) != len(set(value)):
            raise ValueError("deferred_question_ids must be unique")
        return value

    @model_validator(mode="after")
    def validate_session_sequence(self) -> IntakeSession:
        if self.updated_at < self.started_at:
            raise ValueError("updated_at must not be earlier than started_at")
        sequences = [interaction.sequence for interaction in self.interactions]
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("interaction sequence must be contiguous and start at 1")
        return self

    @property
    def metrics(self) -> IntakeMetrics:
        return calculate_metrics(self.interactions)


def calculate_metrics(
    interactions: tuple[IntakeInteraction, ...],
) -> IntakeMetrics:
    """Calculate operator-effort metrics without mutating session state."""

    return IntakeMetrics(
        interaction_count=len(interactions),
        provided_count=sum(
            item.action is IntakeAnswerAction.PROVIDE for item in interactions
        ),
        confirmed_count=sum(
            item.action is IntakeAnswerAction.CONFIRM for item in interactions
        ),
        unknown_count=sum(
            item.action is IntakeAnswerAction.UNKNOWN for item in interactions
        ),
        skipped_count=sum(
            item.action is IntakeAnswerAction.SKIP for item in interactions
        ),
        active_seconds=round(sum(item.active_seconds for item in interactions), 3),
    )
