
"""Strict contracts for knowledge reuse and incremental expansion version 0.1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.adaptation.models import RelativePath, Sha256
from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.expansion.enums import (
    ExpansionDisposition,
    ExpansionPlanStatus,
    ExpansionReasonCode,
    ExpansionReviewDecision,
    ExpansionRunStatus,
    ExpansionSubjectKind,
)

SubjectRef = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[A-Za-z0-9_.\[\]-]+$"),
]


class ExpansionRequest(ContractModel):
    """One human request to add a bounded process using accepted project knowledge."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    base_context_id: Identifier
    base_context_sha256: Sha256
    workspace_profile_id: Identifier
    framework_snapshot_id: Identifier
    framework_snapshot_fingerprint: Sha256
    target_process_id: Identifier
    target_process_name: NonEmptyText
    human_intent: NonEmptyText
    target_element_ids: tuple[Identifier, ...] = Field(min_length=1, max_length=10)
    requested_at: datetime
    proactive_report_id: Identifier | None = None
    human_triggered: Literal[True] = True
    secret_values_included: Literal[False] = False
    live_llm_required: Literal[False] = False

    @field_validator("requested_at")
    @classmethod
    def requested_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("requested_at must include a timezone offset")
        return value

    @field_validator("target_element_ids")
    @classmethod
    def target_ids_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("target_element_ids must be unique")
        return value


class ExpansionPlanItem(ContractModel):
    id: Identifier
    subject_kind: ExpansionSubjectKind
    subject_ref: SubjectRef
    source_id: Identifier | None = None
    knowledge_status: KnowledgeStatus | None = None
    disposition: ExpansionDisposition
    reason_code: ExpansionReasonCode
    evidence_ids: tuple[Identifier, ...] = ()

    @field_validator("evidence_ids")
    @classmethod
    def evidence_ids_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("expansion item evidence ids must be unique")
        return value

    @model_validator(mode="after")
    def validate_status_boundary(self) -> "ExpansionPlanItem":
        if self.subject_kind is ExpansionSubjectKind.FRAMEWORK_SNAPSHOT:
            if self.knowledge_status is not None or self.evidence_ids:
                raise ValueError("framework snapshot item must not masquerade as context knowledge")
        elif self.disposition is ExpansionDisposition.REUSE and self.knowledge_status not in {
            KnowledgeStatus.CONFIRMED,
            KnowledgeStatus.OBSERVED,
        }:
            raise ValueError("reused context knowledge must already be confirmed or observed")
        return self


class ExpansionPlan(ContractModel):
    """Inspectable reuse/gap decision before any expansion observation or generation."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    request_id: Identifier
    base_context_id: Identifier
    base_context_sha256: Sha256
    workspace_profile_id: Identifier
    framework_snapshot_id: Identifier
    framework_snapshot_fingerprint: Sha256
    created_at: datetime
    status: ExpansionPlanStatus = ExpansionPlanStatus.READY_FOR_REVIEW
    decision: ExpansionReviewDecision = ExpansionReviewDecision.PENDING
    items: tuple[ExpansionPlanItem, ...] = Field(min_length=1)
    reuse_count: int = Field(ge=0)
    ask_human_count: int = Field(ge=0)
    observe_new_count: int = Field(ge=0)
    reobserve_count: int = Field(ge=0)
    review_count: int = Field(ge=0)
    blocked_count: int = Field(ge=0)
    bootstrap_questions_repeated: Literal[False] = False
    automatic_context_write_allowed: Literal[False] = False
    phoenixqa_healing_allowed: Literal[False] = False
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)

    @field_validator("created_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("expansion plan timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_plan(self) -> "ExpansionPlan":
        ids = [item.id for item in self.items]
        if len(ids) != len(set(ids)):
            raise ValueError("expansion plan item ids must be unique")
        declared = {
            ExpansionDisposition.REUSE: self.reuse_count,
            ExpansionDisposition.ASK_HUMAN: self.ask_human_count,
            ExpansionDisposition.OBSERVE_NEW: self.observe_new_count,
            ExpansionDisposition.REOBSERVE: self.reobserve_count,
            ExpansionDisposition.REVIEW: self.review_count,
            ExpansionDisposition.BLOCKED: self.blocked_count,
        }
        for disposition, count in declared.items():
            actual = sum(item.disposition is disposition for item in self.items)
            if actual != count:
                raise ValueError(f"{disposition.value}_count does not match plan items")
        if self.status is ExpansionPlanStatus.BLOCKED:
            if not self.blocked_count:
                raise ValueError("blocked expansion plan requires at least one blocked item")
            if self.decision is not ExpansionReviewDecision.PENDING:
                raise ValueError("blocked plan must keep pending decision")
        elif self.status is ExpansionPlanStatus.READY_FOR_REVIEW:
            if self.blocked_count:
                raise ValueError("ready expansion plan cannot contain blocked items")
            if self.decision is not ExpansionReviewDecision.PENDING:
                raise ValueError("ready expansion plan must keep pending decision")
        elif self.status is ExpansionPlanStatus.ACCEPTED:
            if self.decision is not ExpansionReviewDecision.ACCEPTED:
                raise ValueError("accepted expansion plan requires accepted decision")
        elif self.status is ExpansionPlanStatus.REJECTED:
            if self.decision is not ExpansionReviewDecision.REJECTED:
                raise ValueError("rejected expansion plan requires rejected decision")
        if self.decision is ExpansionReviewDecision.PENDING:
            if self.reviewed_at is not None or self.review_reason is not None or self.review_seconds != 0.0:
                raise ValueError("pending expansion plan must not contain review metadata")
        else:
            if self.reviewed_at is None:
                raise ValueError("reviewed expansion plan requires reviewed_at")
            if self.decision is ExpansionReviewDecision.REJECTED and not self.review_reason:
                raise ValueError("rejected expansion plan requires a reason")
        return self


class ExpansionRun(ContractModel):
    """Cross-stage evidence ledger for one incremental expansion."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    request_id: Identifier
    plan_id: Identifier
    base_context_id: Identifier
    base_context_sha256: Sha256
    candidate_context_id: Identifier
    candidate_context_sha256: Sha256
    framework_snapshot_id: Identifier
    framework_snapshot_fingerprint: Sha256
    started_at: datetime
    finished_at: datetime | None = None
    status: ExpansionRunStatus = ExpansionRunStatus.PENDING
    synthesis_run_id: Identifier | None = None
    adaptation_plan_id: Identifier | None = None
    code_patch_id: Identifier | None = None
    application_report_id: Identifier | None = None
    target_test: RelativePath | None = None
    bootstrap_questions_repeated: Literal[False] = False
    reused_knowledge_item_count: int = Field(ge=0)
    process_specific_questions_asked: int = Field(ge=0)
    new_observation_count: int = Field(ge=0)
    reobservation_count: int = Field(ge=0)
    review_item_count: int = Field(ge=0)
    blocked_item_count: int = Field(ge=0)
    framework_symbols_reused: int = Field(ge=0)
    framework_symbols_extended: int = Field(ge=0)
    framework_symbols_added: int = Field(ge=0)
    existing_tests_preserved: int = Field(ge=0)
    new_tests_added: int = Field(ge=0)
    operator_action_count: int = Field(ge=0)
    active_operator_seconds: float = Field(ge=0.0)
    browser_seconds: float = Field(ge=0.0)
    verification_seconds: float = Field(ge=0.0)
    live_llm_calls: int = Field(ge=0)
    interactive_human_trigger_used: bool
    headed_browser_used: bool
    fixture_decisions_used: bool
    candidate_context_reviewed: bool
    existing_creation_pipeline_reused: bool
    existing_page_object_extended: bool
    method_property_collision_protection: bool
    hash_bound_source_replacement_used: bool
    source_drift_preflight_enforced: bool
    framework_execution_independent: bool
    base_context_unchanged: bool
    original_framework_unchanged: bool
    stale_knowledge_silently_reused: Literal[False] = False
    automatic_context_write_performed: Literal[False] = False
    phoenixqa_healing_used: Literal[False] = False
    raw_page_persisted: Literal[False] = False
    measured_savings_claimed: Literal[False] = False

    @field_validator("started_at", "finished_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("expansion run timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_run(self) -> "ExpansionRun":
        if self.finished_at is not None and self.finished_at < self.started_at:
            raise ValueError("finished_at cannot precede started_at")
        if self.interactive_human_trigger_used and self.fixture_decisions_used:
            raise ValueError("real human expansion run cannot use fixture decisions")
        if self.interactive_human_trigger_used and not self.headed_browser_used:
            raise ValueError("real human expansion run requires headed browser evidence")
        if self.status is ExpansionRunStatus.PASSED:
            required = (
                self.finished_at,
                self.synthesis_run_id,
                self.adaptation_plan_id,
                self.code_patch_id,
                self.application_report_id,
                self.target_test,
            )
            if any(value is None for value in required):
                raise ValueError("passed expansion run requires all downstream artefact references")
            if self.blocked_item_count:
                raise ValueError("passed expansion run cannot retain blocked items")
            if self.existing_tests_preserved < 1 or self.new_tests_added < 1:
                raise ValueError("passed expansion run requires preserved and newly added tests")
            if not self.candidate_context_reviewed:
                raise ValueError("passed expansion run requires reviewed candidate context")
            if not self.existing_creation_pipeline_reused:
                raise ValueError("passed expansion run requires reuse of the existing creation pipeline")
            if self.framework_symbols_extended < 1 or not self.existing_page_object_extended:
                raise ValueError("passed expansion run requires an existing framework symbol extension")
            if not self.method_property_collision_protection:
                raise ValueError("passed expansion run requires method/property collision protection")
            if not self.hash_bound_source_replacement_used:
                raise ValueError("passed expansion run requires hash-bound existing-file replacement")
            if not self.source_drift_preflight_enforced:
                raise ValueError("passed expansion run requires source-drift preflight enforcement")
            if not self.framework_execution_independent:
                raise ValueError("passed expansion run requires independent framework execution")
            if not self.base_context_unchanged or not self.original_framework_unchanged:
                raise ValueError("passed expansion run requires unchanged base context and original framework")
        return self


class ExpansionAssessment(ContractModel):
    """Deterministic assessment of the controlled Sprint 14 proof boundary."""

    schema_version: Literal["0.1"] = "0.1"
    run_id: Identifier
    blockers: tuple[NonEmptyText, ...]
    expansion_verified: bool
    controlled_demo_ready: bool
