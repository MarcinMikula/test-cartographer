"""Strict provider-neutral contracts for live LLM-guided intake."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, field_validator, model_validator

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.guided_intake.enums import (
    GuidanceProviderKind,
    GuidedAnswerShape,
    GuidedIntakePhase,
    GuidedIntakeRunState,
)
from test_cartographer.intake.enums import IntakeQuestionKind


class GuidedIntakeProfile(ContractModel):
    """Local provider configuration and data-boundary policy."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    provider: GuidanceProviderKind
    model: NonEmptyText
    base_url: NonEmptyText
    timeout_seconds: float = Field(default=120.0, gt=0.0, le=600.0)
    max_rounds: int = Field(default=4, ge=1, le=20)
    max_prompt_characters: int = Field(default=12_000, ge=1_000, le=100_000)
    max_response_characters: int = Field(default=8_000, ge=500, le=50_000)
    max_output_tokens: int = Field(default=768, ge=128, le=2_048)
    keep_alive_seconds: int = Field(default=900, ge=60, le=3_600)
    allowed_sensitivities: tuple[SensitivityLevel, ...] = (
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
    )
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    seed: int = Field(default=42, ge=0)
    cloud_allowed: Literal[False] = False
    structured_output_required: Literal[True] = True
    raw_prompts_persisted: Literal[False] = False
    raw_responses_persisted: Literal[False] = False

    @field_validator("allowed_sensitivities")
    @classmethod
    def sensitivities_must_be_unique(
        cls, value: tuple[SensitivityLevel, ...]
    ) -> tuple[SensitivityLevel, ...]:
        if not value:
            raise ValueError("allowed_sensitivities must not be empty")
        if len(value) != len(set(value)):
            raise ValueError("allowed_sensitivities must be unique")
        return value

    @model_validator(mode="after")
    def require_local_ollama(self) -> "GuidedIntakeProfile":
        parsed = urlparse(self.base_url)
        if self.provider is GuidanceProviderKind.OLLAMA:
            if parsed.scheme != "http":
                raise ValueError("Ollama guided intake requires local HTTP")
            if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("Ollama guided intake requires a loopback host")
            if parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError("Ollama base_url must not contain credentials or query data")
            if parsed.path not in {"", "/"} or parsed.params:
                raise ValueError("Ollama base_url must point to the local API root")
            if "cloud" in self.model.casefold():
                raise ValueError("cloud model names are not allowed in guided intake")
        return self


class GuidanceCandidate(ContractModel):
    question_id: Identifier
    kind: IntakeQuestionKind
    base_prompt: NonEmptyText
    target_path: NonEmptyText
    current_value: NonEmptyText | None = None


class GuidanceKnownField(ContractModel):
    path: NonEmptyText
    status: NonEmptyText
    value: NonEmptyText | None = None


class GuidanceRequest(ContractModel):
    phase: GuidedIntakePhase
    context_id: Identifier
    initial_request: NonEmptyText
    known_fields: tuple[GuidanceKnownField, ...]
    candidates: tuple[GuidanceCandidate, ...] = Field(min_length=1)
    prohibited_requests: tuple[NonEmptyText, ...] = Field(min_length=1)


class GuidedQuestionPlanItem(ContractModel):
    question_id: Identifier
    user_prompt: NonEmptyText
    reason: NonEmptyText
    answer_shape: GuidedAnswerShape


class GuidedInterviewPlan(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    phase: GuidedIntakePhase
    questions: tuple[GuidedQuestionPlanItem, ...] = Field(min_length=1)

    @field_validator("questions")
    @classmethod
    def question_ids_must_be_unique(
        cls, value: tuple[GuidedQuestionPlanItem, ...]
    ) -> tuple[GuidedQuestionPlanItem, ...]:
        ids = [item.question_id for item in value]
        if len(ids) != len(set(ids)):
            raise ValueError("guided question IDs must be unique")
        return value


class GuidedIntakeTurn(ContractModel):
    sequence: int = Field(ge=1)
    phase: GuidedIntakePhase
    provider: GuidanceProviderKind
    model: NonEmptyText
    candidate_question_ids: tuple[Identifier, ...] = Field(min_length=1)
    planned_question_ids: tuple[Identifier, ...] = Field(min_length=1)
    started_at: datetime
    completed_at: datetime
    latency_seconds: float = Field(ge=0.0)
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    prompt_characters: int = Field(ge=1)
    response_characters: int = Field(ge=1)
    raw_prompt_persisted: Literal[False] = False
    raw_response_persisted: Literal[False] = False

    @model_validator(mode="after")
    def validate_turn(self) -> "GuidedIntakeTurn":
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("turn timestamps must include timezone offsets")
        if self.completed_at.tzinfo is None or self.completed_at.utcoffset() is None:
            raise ValueError("turn timestamps must include timezone offsets")
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")
        if set(self.candidate_question_ids) != set(self.planned_question_ids):
            raise ValueError("the plan must contain every candidate exactly once")
        return self


class GuidedIntakeRun(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    seed_id: Identifier
    session_id: Identifier
    context_id: Identifier
    state: GuidedIntakeRunState
    started_at: datetime
    updated_at: datetime
    turns: tuple[GuidedIntakeTurn, ...] = ()
    live_provider_used: bool = False
    raw_prompts_persisted: Literal[False] = False
    raw_responses_persisted: Literal[False] = False

    @model_validator(mode="after")
    def validate_run(self) -> "GuidedIntakeRun":
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("run timestamps must include timezone offsets")
        if self.updated_at.tzinfo is None or self.updated_at.utcoffset() is None:
            raise ValueError("run timestamps must include timezone offsets")
        if self.updated_at < self.started_at:
            raise ValueError("updated_at must not precede started_at")
        sequences = [turn.sequence for turn in self.turns]
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("turn sequence must be contiguous and start at 1")
        if self.live_provider_used and not any(
            turn.provider is GuidanceProviderKind.OLLAMA for turn in self.turns
        ):
            raise ValueError("live_provider_used requires at least one Ollama turn")
        return self
