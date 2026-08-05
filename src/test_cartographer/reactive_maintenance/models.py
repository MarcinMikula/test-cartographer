"""Strict contracts for a bounded human-triggered reactive-maintenance flow."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Literal

from pydantic import ConfigDict, Field, field_validator, model_validator

from test_cartographer.adaptation.models import PythonName, RelativePath, Sha256
from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.execution.enums import ExecutionAction
from test_cartographer.reactive_maintenance.enums import (
    MaintenanceActionKind,
    MaintenanceDecision,
    MaintenanceDisposition,
    MaintenanceStatus,
)


class ReactiveMaintenanceProfile(ContractModel):
    """Non-secret policy for one controlled maintenance slice."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    label: NonEmptyText
    target_test: RelativePath
    target_source_path: RelativePath
    target_symbol: PythonName
    target_element_id: Identifier
    target_locator_id: Identifier
    expected_action: Literal[ExecutionAction.CLICK] = ExecutionAction.CLICK
    old_locator_strategy: Literal[LocatorStrategy.TEST_ID] = LocatorStrategy.TEST_ID
    old_locator_value: NonEmptyText
    expected_semantic_role: NonEmptyText
    expected_semantic_name: NonEmptyText
    require_complete_traceability: Literal[True] = True
    require_headed_browser: Literal[True] = True
    require_exact_patch_review: Literal[True] = True
    live_llm_allowed: Literal[False] = False
    automatic_original_repository_write_allowed: Literal[False] = False
    raw_failure_text_persisted: Literal[False] = False
    raw_page_persisted: Literal[False] = False
    screenshots_persisted: Literal[False] = False
    sensitivity: Literal[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL] = (
        SensitivityLevel.INTERNAL
    )


class MaintenanceEvidenceAssessment(ContractModel):
    bundle_id: Identifier
    record_id: Identifier | None = None
    disposition: MaintenanceDisposition
    issue_codes: tuple[Identifier, ...] = ()
    failure_is_evidence_not_diagnosis: Literal[True] = True
    application_bug_claimed: Literal[False] = False
    stale_locator_claimed: bool = False
    infrastructure_error_excluded: bool = False
    complete_traceability: bool = False
    matching_last_step: bool = False
    ready_for_reobservation: bool = False


class MaintenanceCandidate(ContractModel):
    id: Identifier
    semantic_role: NonEmptyText
    semantic_name: NonEmptyText
    locator_strategy: LocatorStrategy
    locator_value: NonEmptyText
    match_count: int = Field(ge=1)
    visible: Literal[True] = True
    enabled: bool
    attributes: tuple[NonEmptyText, ...] = ()
    source_record_id: Identifier
    old_locator_absent: bool
    deterministic_match: bool
    human_selection_required: Literal[True] = True

    @field_validator("attributes")
    @classmethod
    def attributes_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("candidate attributes must be unique")
        return value


class MaintenanceDiagnosis(ContractModel):
    id: Identifier
    profile_id: Identifier
    bundle_id: Identifier
    record_id: Identifier
    created_at: datetime
    disposition: Literal[MaintenanceDisposition.REPAIR_CANDIDATE] = (
        MaintenanceDisposition.REPAIR_CANDIDATE
    )
    target_source_path: RelativePath
    target_symbol: PythonName
    old_locator_strategy: LocatorStrategy
    old_locator_value: NonEmptyText
    selected_candidate: MaintenanceCandidate
    candidate_count: int = Field(ge=1)
    human_selected_candidate: Literal[True] = True
    application_bug_claimed: Literal[False] = False
    locator_repair_proposed: Literal[True] = True
    live_llm_used: Literal[False] = False
    raw_page_persisted: Literal[False] = False
    screenshots_persisted: Literal[False] = False

    @field_validator("created_at")
    @classmethod
    def timestamp_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("diagnosis timestamp requires timezone offset")
        return value

    @model_validator(mode="after")
    def candidate_must_change_locator(self) -> "MaintenanceDiagnosis":
        if (
            self.selected_candidate.locator_strategy is self.old_locator_strategy
            and self.selected_candidate.locator_value == self.old_locator_value
        ):
            raise ValueError("maintenance candidate must change the stale locator")
        return self


class MaintenanceSourcePatch(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_assignment=True,
    )

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    diagnosis_id: Identifier
    profile_id: Identifier
    created_at: datetime
    target_path: RelativePath
    symbol_name: PythonName
    expected_before_sha256: Sha256
    old_locator_value: NonEmptyText
    new_locator_value: NonEmptyText
    full_source: str = Field(min_length=1)
    full_source_sha256: Sha256
    expected_after_sha256: Sha256
    status: MaintenanceStatus = MaintenanceStatus.PENDING
    decision: MaintenanceDecision = MaintenanceDecision.PENDING
    exact_source_displayed: bool = False
    omitted_source_lines: Literal[False] = False
    reviewed_at: datetime | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)
    raw_operator_value_persisted: Literal[False] = False
    original_repository_modified: Literal[False] = False
    live_llm_used: Literal[False] = False

    @field_validator("created_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("patch timestamps require timezone offsets")
        return value

    @model_validator(mode="after")
    def validate_patch(self) -> "MaintenanceSourcePatch":
        actual = hashlib.sha256(self.full_source.encode("utf-8")).hexdigest()
        if actual != self.full_source_sha256 or actual != self.expected_after_sha256:
            raise ValueError("maintenance full-source hashes do not match content")
        if self.old_locator_value == self.new_locator_value:
            raise ValueError("maintenance patch must change locator value")
        if self.status is MaintenanceStatus.PENDING:
            if self.decision is not MaintenanceDecision.PENDING:
                raise ValueError("pending patch requires pending decision")
            if self.reviewed_at is not None or self.exact_source_displayed:
                raise ValueError("pending patch cannot claim completed review")
        elif self.status is MaintenanceStatus.PASSED:
            if self.decision is not MaintenanceDecision.ACCEPTED:
                raise ValueError("passed patch requires accepted decision")
            if self.reviewed_at is None or not self.exact_source_displayed:
                raise ValueError("accepted patch requires exact source review")
        elif self.decision is not MaintenanceDecision.REJECTED:
            raise ValueError("rejected patch requires rejected decision")
        return self


class MaintenanceActionRecord(ContractModel):
    sequence: int = Field(ge=1)
    kind: MaintenanceActionKind
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
            raise ValueError("maintenance action timestamps require timezone offsets")
        return value

    @model_validator(mode="after")
    def validate_action(self) -> "MaintenanceActionRecord":
        if self.completed_at < self.started_at:
            raise ValueError("maintenance action completed_at precedes started_at")
        return self


class ReactiveMaintenanceRun(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    status: MaintenanceStatus
    started_at: datetime
    completed_at: datetime
    source_execution_bundle_id: Identifier
    source_failure_record_id: Identifier
    diagnosis_id: Identifier
    patch_id: Identifier
    before_execution_bundle_id: Identifier
    after_execution_bundle_id: Identifier
    actions: tuple[MaintenanceActionRecord, ...] = Field(min_length=1)
    candidate_count: int = Field(ge=1)
    selected_candidate_id: Identifier
    failed_test_count_before: int = Field(ge=1)
    infrastructure_error_count_before: int = Field(ge=0)
    collected_test_count_after: int = Field(ge=1)
    passed_test_count_after: int = Field(ge=1)
    original_framework_unchanged: Literal[True] = True
    sandbox_only_application: Literal[True] = True
    framework_execution_independent: Literal[True] = True
    human_trigger_used: Literal[True] = True
    headed_browser_used: Literal[True] = True
    exact_patch_reviewed: Literal[True] = True
    application_bug_claimed: Literal[False] = False
    live_llm_used: Literal[False] = False
    fixture_decisions_used: Literal[False] = False
    raw_failure_text_persisted: Literal[False] = False
    raw_page_persisted: Literal[False] = False
    raw_operator_values_persisted: Literal[False] = False

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("maintenance run timestamps require timezone offsets")
        return value

    @model_validator(mode="after")
    def validate_run(self) -> "ReactiveMaintenanceRun":
        if self.completed_at < self.started_at:
            raise ValueError("maintenance run completed_at precedes started_at")
        sequences = [item.sequence for item in self.actions]
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("maintenance actions must be contiguous and start at 1")
        if self.status is MaintenanceStatus.PASSED:
            required = set(MaintenanceActionKind)
            present = {item.kind for item in self.actions}
            if not required.issubset(present):
                raise ValueError("passed maintenance run requires every operator boundary")
            if self.passed_test_count_after < 1:
                raise ValueError("passed maintenance run requires a passing rerun")
        return self

    @property
    def operator_action_count(self) -> int:
        return len(self.actions)

    @property
    def active_seconds(self) -> float:
        return round(sum(item.active_seconds for item in self.actions), 3)


class ReactiveMaintenanceAssessment(ContractModel):
    run_id: Identifier
    reactive_maintenance_verified: bool
    controlled_demo_ready: bool
    blockers: tuple[Identifier, ...] = ()
