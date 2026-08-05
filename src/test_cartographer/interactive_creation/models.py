"""Strict audit contracts for the human-operated Creation Flow."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.interactive_creation.enums import (
    InteractiveSessionState,
    OperatorActionKind,
)


class InteractiveCreationProfile(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    label: NonEmptyText
    target_test: NonEmptyText
    require_live_local_llm: Literal[True] = True
    require_headed_browser: Literal[True] = True
    fixture_answers_allowed: Literal[False] = False
    raw_operator_values_persisted: Literal[False] = False
    minimum_intake_answers: int = Field(default=1, ge=1)
    minimum_intake_confirmations: int = Field(default=1, ge=1)
    minimum_review_decisions: int = Field(default=4, ge=1)


class OperatorActionRecord(ContractModel):
    sequence: int = Field(ge=1)
    kind: OperatorActionKind
    target_id: NonEmptyText
    decision: NonEmptyText
    started_at: datetime
    completed_at: datetime
    active_seconds: float = Field(ge=0.0)
    raw_value_persisted: Literal[False] = False

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("operator-action timestamps require timezone offsets")
        return value

    @model_validator(mode="after")
    def validate_action(self) -> "OperatorActionRecord":
        if self.completed_at < self.started_at:
            raise ValueError("operator action completed_at precedes started_at")
        return self


class InteractiveOperatorSession(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    state: InteractiveSessionState
    started_at: datetime
    updated_at: datetime
    creation_flow_run_id: Identifier | None = None
    actions: tuple[OperatorActionRecord, ...] = ()
    interactive_human_trigger_used: Literal[True] = True
    fixture_answers_used: Literal[False] = False
    headed_browser_used: bool = False
    raw_operator_values_persisted: Literal[False] = False

    @field_validator("started_at", "updated_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("interactive-session timestamps require timezone offsets")
        return value

    @model_validator(mode="after")
    def validate_session(self) -> "InteractiveOperatorSession":
        if self.updated_at < self.started_at:
            raise ValueError("interactive session updated_at precedes started_at")
        sequences = [action.sequence for action in self.actions]
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("operator action sequence must be contiguous and start at 1")
        if self.state is InteractiveSessionState.COMPLETE:
            if self.creation_flow_run_id is None:
                raise ValueError("complete interactive session requires a creation-flow run")
            if not self.headed_browser_used:
                raise ValueError("complete interactive session requires a headed browser")
        return self

    @property
    def active_seconds(self) -> float:
        return round(sum(item.active_seconds for item in self.actions), 3)

    @property
    def initial_trigger_count(self) -> int:
        return sum(
            item.kind is OperatorActionKind.INITIAL_REQUEST for item in self.actions
        )

    @property
    def execution_trigger_count(self) -> int:
        return sum(
            item.kind is OperatorActionKind.EXECUTION_TRIGGER for item in self.actions
        )

    @property
    def answer_count(self) -> int:
        return sum(item.kind is OperatorActionKind.INTAKE_ANSWER for item in self.actions)

    @property
    def confirmation_count(self) -> int:
        return sum(
            item.kind is OperatorActionKind.INTAKE_CONFIRMATION for item in self.actions
        )

    @property
    def handoff_confirmation_count(self) -> int:
        return sum(
            item.kind is OperatorActionKind.SYNTHESIS_HANDOFF_CONFIRMATION
            for item in self.actions
        )

    @property
    def ambiguity_selection_count(self) -> int:
        return sum(
            item.kind is OperatorActionKind.AMBIGUITY_SELECTION for item in self.actions
        )

    @property
    def review_decision_count(self) -> int:
        return sum(item.kind is OperatorActionKind.REVIEW_DECISION for item in self.actions)
class ExactPatchRereviewReport(ContractModel):
    """Audit proof for a post-run exact patch re-review."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    creation_flow_run_id: Identifier
    original_patch_id: Identifier
    corrected_patch_id: Identifier
    started_at: datetime
    completed_at: datetime
    decision: Literal["accepted"]
    exact_source_displayed: Literal[True] = True
    omitted_source_lines: Literal[False] = False
    deterministic_navigation_docstring_used: Literal[True] = True
    ambiguity_question_deterministically_completed: bool
    llm_role_disclosed: Literal[True] = True
    deterministic_synthesis_disclosed: Literal[True] = True
    change_count: int = Field(ge=1)
    operator_review_seconds: float = Field(ge=0.0)
    collected_test_count: int = Field(ge=1)
    passed_test_count: int = Field(ge=1)
    original_framework_unchanged: Literal[True] = True
    raw_operator_values_persisted: Literal[False] = False

    @field_validator("started_at", "completed_at")
    @classmethod
    def rereview_timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("patch re-review timestamps require timezone offsets")
        return value

    @model_validator(mode="after")
    def validate_rereview(self) -> "ExactPatchRereviewReport":
        if self.completed_at < self.started_at:
            raise ValueError("patch re-review completed_at precedes started_at")
        if self.passed_test_count > self.collected_test_count:
            raise ValueError("passed tests cannot exceed collected tests")
        return self
