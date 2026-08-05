"""Strict contracts for the Sprint 10 integrated Creation Flow."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.creation_flow.enums import (
    CreationFlowStatus,
    CreationStageKind,
    CreationStageStatus,
)


class CreationFlowProfile(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    label: NonEmptyText
    minimal_request: NonEmptyText
    target_test: NonEmptyText
    expected_answer_count: int = Field(ge=1)
    expected_confirmation_count: int = Field(ge=1)
    expected_handoff_confirmation_count: int = Field(ge=1)
    expected_ambiguity_resolution_count: int = Field(ge=1)
    expected_review_decision_count: int = Field(ge=1)
    fixture_assisted_reference_demo: Literal[True] = True
    live_intake_required: Literal[True] = True
    live_discovery_guidance_required: Literal[True] = True
    deterministic_synthesis_template: Literal[True] = True
    measured_savings_claimed: Literal[False] = False


class CreationStageRecord(ContractModel):
    kind: CreationStageKind
    status: CreationStageStatus
    started_at: datetime
    completed_at: datetime
    duration_seconds: float = Field(ge=0.0)
    live_llm_calls: int = Field(default=0, ge=0)
    deterministic_operations: int = Field(default=0, ge=0)
    browser_operations: int = Field(default=0, ge=0)
    human_actions: int = Field(default=0, ge=0)
    artifact_ids: tuple[Identifier, ...] = ()
    summary: NonEmptyText

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("creation-stage timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_stage(self) -> "CreationStageRecord":
        if self.completed_at < self.started_at:
            raise ValueError("creation stage completed_at precedes started_at")
        return self


class CreationFlowRun(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    context_id: Identifier
    status: CreationFlowStatus
    started_at: datetime
    completed_at: datetime
    target_test: NonEmptyText
    stages: tuple[CreationStageRecord, ...] = Field(min_length=7, max_length=7)
    total_seconds: float = Field(ge=0.0)
    model_seconds: float = Field(ge=0.0)
    browser_seconds: float = Field(ge=0.0)
    verification_seconds: float = Field(ge=0.0)
    human_active_seconds: float = Field(ge=0.0)
    live_llm_call_count: int = Field(ge=0)
    deterministic_synthesis_call_count: int = Field(ge=0)
    human_trigger_count: int = Field(default=0, ge=0)
    human_answer_count: int = Field(ge=0)
    human_confirmation_count: int = Field(ge=0)
    handoff_confirmation_count: int = Field(ge=0)
    ambiguity_resolution_count: int = Field(ge=0)
    review_decision_count: int = Field(ge=0)
    execution_trigger_count: int = Field(default=0, ge=0)
    total_human_action_count: int = Field(ge=0)
    candidate_count: int = Field(ge=0)
    target_count: int = Field(ge=0)
    generated_file_count: int = Field(ge=0)
    modified_file_count: int = Field(ge=0)
    reused_symbol_count: int = Field(ge=0)
    collected_test_count: int = Field(ge=0)
    passed_test_count: int = Field(ge=0)
    fixture_assisted_reference_demo: bool = True
    interactive_human_used_during_verifier: bool = False
    live_llm_used: bool
    deterministic_synthesis_template_used: Literal[True] = True
    raw_prompts_persisted: Literal[False] = False
    raw_responses_persisted: Literal[False] = False
    human_answer_values_persisted_in_run: Literal[False] = False
    framework_execution_independent: bool
    original_framework_unchanged: bool
    full_traceability: bool
    measured_savings_claimed: Literal[False] = False

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("creation-flow timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_run(self) -> "CreationFlowRun":
        expected = tuple(CreationStageKind)
        actual = tuple(stage.kind for stage in self.stages)
        if actual != expected:
            raise ValueError(f"creation stages must use the canonical order: {expected}")
        if self.completed_at < self.started_at:
            raise ValueError("creation flow completed_at precedes started_at")
        summed = (
            self.human_trigger_count
            + self.human_answer_count
            + self.human_confirmation_count
            + self.handoff_confirmation_count
            + self.ambiguity_resolution_count
            + self.review_decision_count
            + self.execution_trigger_count
        )
        if self.total_human_action_count != summed:
            raise ValueError("total_human_action_count does not match its components")
        if self.fixture_assisted_reference_demo and self.interactive_human_used_during_verifier:
            raise ValueError("creation flow cannot be fixture-assisted and interactive at once")
        if self.status is CreationFlowStatus.PASSED:
            checks = (
                all(stage.status is CreationStageStatus.PASSED for stage in self.stages),
                self.live_llm_used,
                self.live_llm_call_count >= 2,
                self.deterministic_synthesis_call_count == 1,
                self.candidate_count >= 3,
                self.target_count >= 3,
                self.generated_file_count >= 3,
                self.modified_file_count >= 1,
                self.collected_test_count >= 1,
                self.passed_test_count >= 1,
                self.framework_execution_independent,
                self.original_framework_unchanged,
                self.full_traceability,
            )
            if not all(checks):
                raise ValueError("passed creation flow requires all demo proof checks")
        return self


class CreationFlowAssessment(ContractModel):
    run_id: Identifier
    creation_mechanics_verified: bool
    ready_for_human_trigger_integration: bool
    ready_for_external_user_demo: bool
    mechanics_blockers: tuple[Identifier, ...] = ()
    external_demo_blockers: tuple[Identifier, ...] = ()
    evidence_statements: tuple[NonEmptyText, ...] = ()
