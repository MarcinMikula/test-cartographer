"""Strict contracts for deterministic source generation, application, and evaluation."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, StringConstraints, field_validator, model_validator

from test_cartographer.adaptation.enums import AdaptationTargetKind, PythonSymbolKind
from test_cartographer.adaptation.models import PythonName, RelativePath, Sha256
from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.delivery.enums import (
    CodePatchStatus,
    CreationEvaluationStatus,
    PatchApplicationStatus,
    PatchReviewDecision,
    SourceChangeKind,
)

EnvironmentVariableName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[A-Z][A-Z0-9_]{2,79}$"),
]
SourceText = Annotated[str, StringConstraints(min_length=1)]


class TestDataBinding(ContractModel):
    test_data_id: Identifier
    fixture_key: PythonName
    value: NonEmptyText
    sensitivity: Literal[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL]
    secret: Literal[False] = False


class FrameworkSymbolRequirement(ContractModel):
    """One framework primitive required by a deterministic generation template."""

    path: RelativePath
    symbol_name: PythonName
    symbol_kind: PythonSymbolKind


class GenerationProfile(ContractModel):
    """Non-secret runtime bindings used by deterministic Sprint 6 templates."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    workspace_profile_id: Identifier
    environment_url_variable: EnvironmentVariableName
    required_framework_symbols: tuple[FrameworkSymbolRequirement, ...] = Field(min_length=1)
    test_data_bindings: tuple[TestDataBinding, ...] = ()
    browser_headless: bool = True
    secret_values_included: Literal[False] = False
    live_llm_used: Literal[False] = False

    @model_validator(mode="after")
    def bindings_must_be_unique(self) -> GenerationProfile:
        requirements = [(item.path, item.symbol_name, item.symbol_kind) for item in self.required_framework_symbols]
        if len(requirements) != len(set(requirements)):
            raise ValueError("framework symbol requirements must be unique")
        data_ids = [item.test_data_id for item in self.test_data_bindings]
        fixture_keys = [item.fixture_key for item in self.test_data_bindings]
        if len(data_ids) != len(set(data_ids)):
            raise ValueError("test-data binding ids must be unique")
        if len(fixture_keys) != len(set(fixture_keys)):
            raise ValueError("test-data fixture keys must be unique")
        return self


class SourceChange(ContractModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_assignment=True,
    )

    operation_id: Identifier
    kind: SourceChangeKind
    target_kind: AdaptationTargetKind
    target_path: RelativePath
    symbol_name: PythonName
    source_proposal_ids: tuple[Identifier, ...] = Field(min_length=1)
    expected_before_sha256: Sha256 | None = None
    content: SourceText
    content_sha256: Sha256
    expected_after_sha256: Sha256

    @field_validator("source_proposal_ids")
    @classmethod
    def source_ids_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("source proposal ids must be unique")
        return value

    @model_validator(mode="after")
    def validate_change(self) -> SourceChange:
        actual = hashlib.sha256(self.content.encode("utf-8")).hexdigest()
        if actual != self.content_sha256:
            raise ValueError("content_sha256 does not match content")
        if self.kind is SourceChangeKind.CREATE_FILE:
            if self.expected_before_sha256 is not None:
                raise ValueError("create_file must not contain expected_before_sha256")
            if self.content_sha256 != self.expected_after_sha256:
                raise ValueError("create_file after hash must equal content hash")
        elif self.expected_before_sha256 is None:
            raise ValueError("non-create source change requires expected_before_sha256")
        elif self.kind is SourceChangeKind.REPLACE_FILE and self.content_sha256 != self.expected_after_sha256:
            raise ValueError("replace_file after hash must equal full replacement content hash")
        return self


class ReusedTarget(ContractModel):
    operation_id: Identifier
    target_kind: AdaptationTargetKind
    target_path: RelativePath
    symbol_name: PythonName


class CodePatch(ContractModel):
    """Exact generated source proposal. It cannot write to the framework itself."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    plan_id: Identifier
    workspace_profile_id: Identifier
    generation_profile_id: Identifier
    snapshot_id: Identifier
    snapshot_fingerprint: Sha256
    synthesis_run_id: Identifier
    proposal_id: Identifier
    context_id: Identifier
    created_at: datetime
    status: CodePatchStatus = CodePatchStatus.READY_FOR_REVIEW
    decision: PatchReviewDecision = PatchReviewDecision.PENDING
    changes: tuple[SourceChange, ...] = Field(min_length=1)
    reused_targets: tuple[ReusedTarget, ...] = ()
    verification_commands: tuple[NonEmptyText, ...] = Field(min_length=1)
    generated_source_included: Literal[True] = True
    secret_values_included: Literal[False] = False
    live_llm_used: Literal[False] = False
    framework_files_modified: Literal[False] = False
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)

    @field_validator("created_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("delivery timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_patch(self) -> CodePatch:
        operation_ids = [item.operation_id for item in self.changes] + [
            item.operation_id for item in self.reused_targets
        ]
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("delivery operation ids must be unique")
        paths = [item.target_path for item in self.changes]
        if len(paths) != len(set(paths)):
            raise ValueError("a code patch may change each target path only once")

        if self.status is CodePatchStatus.READY_FOR_REVIEW:
            if self.decision is not PatchReviewDecision.PENDING:
                raise ValueError("ready code patch must keep pending decision")
        elif self.status is CodePatchStatus.ACCEPTED:
            if self.decision is not PatchReviewDecision.ACCEPTED:
                raise ValueError("accepted code patch requires accepted decision")
        elif self.decision is not PatchReviewDecision.REJECTED:
            raise ValueError("rejected code patch requires rejected decision")

        if self.decision is PatchReviewDecision.PENDING:
            if self.reviewed_at is not None or self.review_reason is not None or self.review_seconds != 0.0:
                raise ValueError("pending code patch must not contain review metadata")
        else:
            if self.reviewed_at is None:
                raise ValueError("reviewed code patch requires reviewed_at")
            if self.decision is PatchReviewDecision.REJECTED and not self.review_reason:
                raise ValueError("rejected code patch requires a reason")
        return self


class AppliedChange(ContractModel):
    operation_id: Identifier
    target_path: RelativePath
    before_sha256: Sha256 | None = None
    after_sha256: Sha256
    bytes_written: int = Field(ge=1)


class PatchApplicationReport(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    patch_id: Identifier
    plan_id: Identifier
    snapshot_id: Identifier
    snapshot_fingerprint: Sha256
    applied_at: datetime
    application_seconds: float = Field(ge=0.0)
    status: Literal[PatchApplicationStatus.APPLIED] = PatchApplicationStatus.APPLIED
    changes: tuple[AppliedChange, ...] = Field(min_length=1)
    after_fingerprint: Sha256
    preflight_passed: Literal[True] = True
    rollback_performed: Literal[False] = False
    workspace_files_modified: Literal[True] = True
    target_root_persisted: Literal[False] = False
    verification_pending: Literal[True] = True

    @field_validator("applied_at")
    @classmethod
    def applied_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("applied_at must include a timezone offset")
        return value


class VerificationResult(ContractModel):
    name: Identifier
    command: NonEmptyText
    exit_code: int
    duration_seconds: float = Field(ge=0.0)
    output_sha256: Sha256
    passed: bool


class CreationEvaluation(ContractModel):
    """Measured evidence for the first complete automation-creation lifecycle."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    context_id: Identifier
    synthesis_run_id: Identifier
    adaptation_plan_id: Identifier
    code_patch_id: Identifier
    application_report_id: Identifier
    completed_at: datetime
    status: CreationEvaluationStatus
    target_test: RelativePath
    generated_file_count: int = Field(ge=0)
    modified_file_count: int = Field(ge=0)
    reused_symbol_count: int = Field(ge=0)
    collected_test_count: int = Field(ge=0)
    passed_test_count: int = Field(ge=0)
    synthesis_review_seconds: float = Field(ge=0.0)
    adaptation_review_seconds: float = Field(ge=0.0)
    code_review_seconds: float = Field(ge=0.0)
    application_seconds: float = Field(ge=0.0)
    verification_seconds: float = Field(ge=0.0)
    time_to_first_runnable_test_seconds: float = Field(ge=0.0)
    llm_call_count: Literal[0] = 0
    live_llm_used: Literal[False] = False
    page_object_generated: bool
    component_required: bool = True
    component_generated: bool
    fixture_generated: bool
    test_generated: bool
    meaningful_test_assertion_present: bool
    framework_execution_independent: bool
    original_framework_unchanged: bool
    verification_results: tuple[VerificationResult, ...] = Field(min_length=1)
    corrections: tuple[NonEmptyText, ...] = ()

    @field_validator("completed_at")
    @classmethod
    def completed_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("completed_at must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_evaluation(self) -> CreationEvaluation:
        all_checks = (
            self.collected_test_count >= 1,
            self.passed_test_count >= 1,
            self.page_object_generated,
            not self.component_required or self.component_generated,
            self.fixture_generated,
            self.test_generated,
            self.meaningful_test_assertion_present,
            self.framework_execution_independent,
            self.original_framework_unchanged,
            all(item.passed for item in self.verification_results),
        )
        if self.status is CreationEvaluationStatus.PASSED and not all(all_checks):
            raise ValueError("passed creation evaluation requires all execution and architecture checks")
        return self
