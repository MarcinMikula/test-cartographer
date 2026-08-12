"""Strict provider-neutral contracts for guided process discovery."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.context.enums import ActionKind, LocatorStrategy, SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.discovery.enums import (
    DiscoveryDecision,
    DiscoveryProviderKind,
    DiscoveryRunState,
    DiscoveryTargetState,
    SelectionAuthority,
)

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
TagName = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9-]*$")]
RoleName = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_-]*$")]


class DiscoveryProfile(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    provider: DiscoveryProviderKind
    model: NonEmptyText
    base_url: NonEmptyText
    timeout_seconds: float = Field(default=300.0, gt=0.0, le=600.0)
    max_elements_scanned: int = Field(default=80, ge=3, le=500)
    max_candidates_per_target: int = Field(default=4, ge=2, le=10)
    minimum_candidate_score: int = Field(default=45, ge=1, le=100)
    ambiguity_score_delta: int = Field(default=3, ge=0, le=25)
    max_prompt_characters: int = Field(default=6_000, ge=500, le=30_000)
    max_response_characters: int = Field(default=2_000, ge=200, le=10_000)
    max_output_tokens: int = Field(default=256, ge=64, le=1_024)
    keep_alive_seconds: int = Field(default=900, ge=60, le=3_600)
    temperature: float = Field(default=0.0, ge=0.0, le=1.0)
    seed: int = Field(default=42, ge=0)
    allowed_sensitivities: tuple[SensitivityLevel, ...] = (
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
    )
    raw_page_persisted: Literal[False] = False
    screenshot_persisted: Literal[False] = False
    html_persisted: Literal[False] = False
    input_values_persisted: Literal[False] = False
    generic_page_text_persisted: Literal[False] = False
    raw_prompts_persisted: Literal[False] = False
    raw_responses_persisted: Literal[False] = False
    cloud_allowed: Literal[False] = False

    @model_validator(mode="after")
    def validate_provider_boundary(self) -> "DiscoveryProfile":
        parsed = urlsplit(self.base_url)
        if self.provider is DiscoveryProviderKind.OLLAMA:
            if parsed.scheme != "http":
                raise ValueError("Ollama discovery guidance requires local HTTP")
            if parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("Ollama discovery guidance requires a loopback host")
            if parsed.username or parsed.password or parsed.query or parsed.fragment:
                raise ValueError("Ollama base_url must not contain credentials or query data")
            if parsed.path not in {"", "/"}:
                raise ValueError("Ollama base_url must point to the local API root")
            if "cloud" in self.model.casefold():
                raise ValueError("cloud model names are not allowed")
        if len(self.allowed_sensitivities) != len(set(self.allowed_sensitivities)):
            raise ValueError("allowed_sensitivities must be unique")
        return self


class DiscoveryTarget(ContractModel):
    id: Identifier
    element_id: Identifier
    owner_id: Identifier
    name: NonEmptyText
    action_kind: ActionKind
    expected_roles: tuple[RoleName, ...] = Field(min_length=1)
    test_data_symbolic_ref: Identifier | None = None
    outcome_target: bool = False

    @model_validator(mode="after")
    def validate_target(self) -> "DiscoveryTarget":
        if self.action_kind in {ActionKind.FILL, ActionKind.SELECT}:
            if self.test_data_symbolic_ref is None:
                raise ValueError("fill/select discovery targets require symbolic test data")
        elif self.test_data_symbolic_ref is not None:
            raise ValueError("only fill/select targets may declare symbolic test data")
        return self


class ProcessDiscoveryPlan(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    context_id: Identifier
    process_id: Identifier
    page_id: Identifier
    page_name: NonEmptyText
    route: NonEmptyText
    source_url: NonEmptyText
    component_ids: tuple[Identifier, ...] = ()
    targets: tuple[DiscoveryTarget, ...] = Field(min_length=1)
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_minimized(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"file", "http", "https"}:
            raise ValueError("source_url must use file, http, or https")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("source_url must not contain credentials, query, or fragment")
        return value

    @model_validator(mode="after")
    def target_ids_must_be_unique(self) -> "ProcessDiscoveryPlan":
        ids = [target.id for target in self.targets]
        element_ids = [target.element_id for target in self.targets]
        if len(ids) != len(set(ids)):
            raise ValueError("discovery target IDs must be unique")
        if len(element_ids) != len(set(element_ids)):
            raise ValueError("discovery element IDs must be unique")
        owners = set(self.component_ids) | {self.page_id}
        unknown = sorted({target.owner_id for target in self.targets} - owners)
        if unknown:
            raise ValueError(f"target owners are not declared by the plan: {unknown}")
        return self


class CandidateAttribute(ContractModel):
    name: NonEmptyText
    value: NonEmptyText


class DiscoveredLocator(ContractModel):
    id: Identifier
    strategy: LocatorStrategy
    value: NonEmptyText
    match_count: int = Field(ge=0)
    priority: int = Field(ge=1, le=100)


class ElementCandidate(ContractModel):
    id: Identifier
    ordinal: int = Field(ge=1)
    tag_name: TagName
    semantic_role: RoleName
    semantic_name: NonEmptyText
    visible: Literal[True] = True
    enabled: bool
    editable: bool
    attributes: tuple[CandidateAttribute, ...] = ()
    locator_candidates: tuple[DiscoveredLocator, ...] = Field(min_length=1)
    input_value_persisted: Literal[False] = False
    raw_text_content_persisted: Literal[False] = False
    html_persisted: Literal[False] = False

    @field_validator("attributes")
    @classmethod
    def attributes_must_be_unique(
        cls, value: tuple[CandidateAttribute, ...]
    ) -> tuple[CandidateAttribute, ...]:
        names = [item.name for item in value]
        if len(names) != len(set(names)):
            raise ValueError("candidate attribute names must be unique")
        return value


class CandidateScore(ContractModel):
    candidate_id: Identifier
    score: int = Field(ge=0, le=100)
    matched_tokens: tuple[NonEmptyText, ...] = ()


class DiscoveryTargetResult(ContractModel):
    target_id: Identifier
    state: DiscoveryTargetState
    ranked_candidates: tuple[CandidateScore, ...] = ()
    selected_candidate_id: Identifier | None = None
    selection_authority: SelectionAuthority | None = None

    @model_validator(mode="after")
    def validate_selection(self) -> "DiscoveryTargetResult":
        ranked_ids = {item.candidate_id for item in self.ranked_candidates}
        if self.state is DiscoveryTargetState.SELECTED:
            if self.selected_candidate_id is None or self.selection_authority is None:
                raise ValueError("selected target requires candidate and authority")
            if self.selected_candidate_id not in ranked_ids:
                raise ValueError("selected candidate must be present in ranking")
        else:
            if self.selected_candidate_id is not None or self.selection_authority is not None:
                raise ValueError("unselected targets must not declare a selection")
        return self


class DiscoveryAmbiguity(ContractModel):
    id: Identifier
    target_id: Identifier
    candidate_ids: tuple[Identifier, ...] = Field(min_length=2)
    question: NonEmptyText | None = None
    selected_candidate_id: Identifier | None = None
    resolved_at: datetime | None = None
    resolution_reason: NonEmptyText | None = None

    @model_validator(mode="after")
    def validate_resolution(self) -> "DiscoveryAmbiguity":
        if len(self.candidate_ids) != len(set(self.candidate_ids)):
            raise ValueError("ambiguity candidate IDs must be unique")
        if self.selected_candidate_id is None:
            if self.resolved_at is not None or self.resolution_reason is not None:
                raise ValueError("unresolved ambiguity must not contain resolution data")
        else:
            if self.selected_candidate_id not in self.candidate_ids:
                raise ValueError("selected ambiguity candidate is not allowed")
            if self.resolved_at is None or self.resolution_reason is None:
                raise ValueError("resolved ambiguity requires time and reason")
        return self


class AmbiguityQuestionPlan(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    ambiguity_id: Identifier
    candidate_ids: tuple[Identifier, ...] = Field(min_length=2)
    user_prompt: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=320)]
    reason: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=240)]

    @field_validator("candidate_ids")
    @classmethod
    def candidate_ids_must_be_unique(
        cls, value: tuple[Identifier, ...]
    ) -> tuple[Identifier, ...]:
        if len(value) != len(set(value)):
            raise ValueError("ambiguity question candidate IDs must be unique")
        return value


class DiscoveryGuidanceTurn(ContractModel):
    sequence: int = Field(ge=1)
    ambiguity_id: Identifier
    provider: DiscoveryProviderKind
    model: NonEmptyText
    candidate_ids: tuple[Identifier, ...] = Field(min_length=2)
    started_at: datetime
    completed_at: datetime
    latency_seconds: float = Field(ge=0.0)
    prompt_sha256: Sha256
    response_sha256: Sha256
    prompt_characters: int = Field(ge=1)
    response_characters: int = Field(ge=1)
    raw_prompt_persisted: Literal[False] = False
    raw_response_persisted: Literal[False] = False

    @model_validator(mode="after")
    def validate_turn(self) -> "DiscoveryGuidanceTurn":
        for value in (self.started_at, self.completed_at):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("guidance timestamps require timezone offsets")
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not precede started_at")
        return self


class ProcessDiscoveryRun(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    plan_id: Identifier
    context_id: Identifier
    source_url: NonEmptyText
    captured_at: datetime
    updated_at: datetime
    capture_seconds: float = Field(default=0.0, ge=0.0)
    state: DiscoveryRunState
    candidates: tuple[ElementCandidate, ...] = Field(min_length=1)
    targets: tuple[DiscoveryTargetResult, ...] = Field(min_length=2)
    ambiguities: tuple[DiscoveryAmbiguity, ...] = ()
    guidance_turns: tuple[DiscoveryGuidanceTurn, ...] = ()
    capture_sha256: Sha256
    decision: DiscoveryDecision = DiscoveryDecision.PENDING
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)
    live_provider_used: bool = False
    raw_page_persisted: Literal[False] = False
    screenshot_persisted: Literal[False] = False
    html_persisted: Literal[False] = False
    input_values_persisted: Literal[False] = False
    generic_page_text_persisted: Literal[False] = False
    raw_prompts_persisted: Literal[False] = False
    raw_responses_persisted: Literal[False] = False

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_minimized(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            raise ValueError("run source_url must be minimized")
        return value

    @model_validator(mode="after")
    def validate_run(self) -> "ProcessDiscoveryRun":
        for value in (self.captured_at, self.updated_at):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("run timestamps require timezone offsets")
        if self.updated_at < self.captured_at:
            raise ValueError("updated_at must not precede captured_at")
        candidate_ids = {candidate.id for candidate in self.candidates}
        target_ids = [target.target_id for target in self.targets]
        if len(target_ids) != len(set(target_ids)):
            raise ValueError("run target IDs must be unique")
        for target in self.targets:
            unknown = {item.candidate_id for item in target.ranked_candidates} - candidate_ids
            if unknown:
                raise ValueError(f"target ranking references unknown candidates: {sorted(unknown)}")
        for ambiguity in self.ambiguities:
            if ambiguity.target_id not in set(target_ids):
                raise ValueError("ambiguity references an unknown target")
            if set(ambiguity.candidate_ids) - candidate_ids:
                raise ValueError("ambiguity references unknown candidates")
        sequences = [turn.sequence for turn in self.guidance_turns]
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("guidance sequence must be contiguous and start at 1")
        if self.live_provider_used and not any(
            turn.provider is DiscoveryProviderKind.OLLAMA for turn in self.guidance_turns
        ):
            raise ValueError("live_provider_used requires an Ollama guidance turn")
        unresolved = [item for item in self.ambiguities if item.selected_candidate_id is None]
        missing = [item for item in self.targets if item.state is DiscoveryTargetState.MISSING]
        if self.state is DiscoveryRunState.AWAITING_RESOLUTION and not unresolved:
            raise ValueError("awaiting_resolution requires an unresolved ambiguity")
        if self.state in {DiscoveryRunState.RESOLVED, DiscoveryRunState.ACCEPTED}:
            if unresolved or missing or any(
                item.state is not DiscoveryTargetState.SELECTED for item in self.targets
            ):
                raise ValueError("resolved/accepted run requires every target selected")
        if self.state is DiscoveryRunState.ACCEPTED and self.decision is not DiscoveryDecision.ACCEPTED:
            raise ValueError("accepted state requires accepted decision")
        if self.state is DiscoveryRunState.REJECTED and self.decision is not DiscoveryDecision.REJECTED:
            raise ValueError("rejected state requires rejected decision")
        if self.decision is DiscoveryDecision.ACCEPTED and self.state is not DiscoveryRunState.ACCEPTED:
            raise ValueError("accepted decision requires accepted state")
        if self.decision is DiscoveryDecision.REJECTED and self.state is not DiscoveryRunState.REJECTED:
            raise ValueError("rejected decision requires rejected state")
        if self.decision is DiscoveryDecision.PENDING:
            if self.reviewed_at is not None or self.review_reason is not None:
                raise ValueError("pending run must not contain review data")
        else:
            if self.reviewed_at is None:
                raise ValueError("reviewed discovery requires reviewed_at")
            if self.reviewed_at < self.captured_at:
                raise ValueError("reviewed_at must not precede capture")
            if self.decision is DiscoveryDecision.REJECTED and self.review_reason is None:
                raise ValueError("rejected discovery requires a reason")
        return self
