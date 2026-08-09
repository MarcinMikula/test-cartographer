"""Strict contracts for a bounded framework snapshot and adaptation plan."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.adaptation.enums import (
    AdaptationOperationKind,
    AdaptationPlanStatus,
    AdaptationReviewDecision,
    AdaptationTargetKind,
    PythonSymbolKind,
    RepositoryEntryKind,
)
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText

RelativePath = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$"),
]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
PythonName = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[A-Za-z_][A-Za-z0-9_]{2,79}$")]


class WorkspaceProfile(ContractModel):
    """Non-secret instructions for inspecting one framework workspace."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    repository_kind: Literal["qa_automation_framework"] = "qa_automation_framework"
    repository_label: NonEmptyText
    root_marker_files: tuple[RelativePath, ...] = Field(min_length=1)
    allowed_roots: tuple[RelativePath, ...] = Field(min_length=1)
    ignored_names: tuple[NonEmptyText, ...] = (
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "allure-results",
    )
    max_files: int = Field(default=500, ge=1, le=5000)
    max_file_bytes: int = Field(default=200_000, ge=1, le=5_000_000)

    @field_validator("root_marker_files", "allowed_roots")
    @classmethod
    def paths_must_be_safe(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for path in value:
            if path.startswith("/") or "\\" in path or ".." in path.split("/"):
                raise ValueError("workspace paths must be safe repository-relative paths")
        return value

    @field_validator("root_marker_files", "allowed_roots", "ignored_names")
    @classmethod
    def entries_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("workspace profile entries must be unique")
        return value


class PythonSymbol(ContractModel):
    kind: PythonSymbolKind
    name: PythonName
    bases: tuple[PythonName, ...] = ()
    method_names: tuple[PythonName, ...] = ()
    property_names: tuple[PythonName, ...] = ()

    @field_validator("bases", "method_names", "property_names")
    @classmethod
    def names_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("python symbol names must be unique")
        return value

    @model_validator(mode="after")
    def method_and_property_names_must_not_overlap(self) -> "PythonSymbol":
        overlap = sorted(set(self.method_names) & set(self.property_names))
        if overlap:
            raise ValueError(f"python symbol method/property names overlap: {overlap}")
        return self


class RepositoryEntry(ContractModel):
    path: RelativePath
    kind: RepositoryEntryKind
    size_bytes: int = Field(ge=0)
    sha256: Sha256 | None = None
    python_symbols: tuple[PythonSymbol, ...] = ()

    @model_validator(mode="after")
    def validate_entry_shape(self) -> RepositoryEntry:
        if self.kind is RepositoryEntryKind.DIRECTORY:
            if self.size_bytes != 0 or self.sha256 is not None or self.python_symbols:
                raise ValueError("directory entry must not contain file metadata")
        elif self.sha256 is None:
            raise ValueError("file entry requires sha256")
        return self


class FrameworkSnapshot(ContractModel):
    """Minimized, replayable repository structure without source-file content."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    captured_at: datetime
    repository_label: NonEmptyText
    root_fingerprint: Sha256
    entries: tuple[RepositoryEntry, ...] = Field(min_length=1)
    source_contents_persisted: Literal[False] = False
    absolute_paths_persisted: Literal[False] = False
    secret_values_persisted: Literal[False] = False

    @field_validator("captured_at")
    @classmethod
    def captured_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone offset")
        return value

    @model_validator(mode="after")
    def entry_paths_must_be_unique(self) -> FrameworkSnapshot:
        paths = [entry.path for entry in self.entries]
        if len(paths) != len(set(paths)):
            raise ValueError("framework snapshot paths must be unique")
        return self


class AdaptationOperation(ContractModel):
    id: Identifier
    kind: AdaptationOperationKind
    target_kind: AdaptationTargetKind
    target_path: RelativePath
    symbol_name: PythonName
    source_proposal_ids: tuple[Identifier, ...] = Field(min_length=1)
    rationale: NonEmptyText
    method_names: tuple[PythonName, ...] = ()
    property_names: tuple[PythonName, ...] = ()
    depends_on: tuple[Identifier, ...] = ()

    @field_validator("source_proposal_ids", "depends_on")
    @classmethod
    def ids_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("adaptation operation references must be unique")
        return value

    @field_validator("method_names", "property_names")
    @classmethod
    def extension_names_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("adaptation extension names must be unique")
        return value

    @model_validator(mode="after")
    def validate_extension_shape(self) -> "AdaptationOperation":
        overlap = sorted(set(self.method_names) & set(self.property_names))
        if overlap:
            raise ValueError(f"adaptation method/property names overlap: {overlap}")
        if self.kind is AdaptationOperationKind.EXTEND_SYMBOL:
            if self.target_kind not in {AdaptationTargetKind.PAGE, AdaptationTargetKind.COMPONENT}:
                raise ValueError("extend_symbol supports page/component classes only")
            if not self.method_names and not self.property_names:
                raise ValueError("extend_symbol requires missing methods or properties")
        elif self.method_names or self.property_names:
            raise ValueError("extension names are only valid for extend_symbol")
        return self


class AdaptationPlan(ContractModel):
    """Exact, reviewable plan that does not contain generated source code."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    workspace_profile_id: Identifier
    snapshot_id: Identifier
    snapshot_fingerprint: Sha256
    synthesis_run_id: Identifier
    proposal_id: Identifier
    context_id: Identifier
    created_at: datetime
    status: AdaptationPlanStatus = AdaptationPlanStatus.READY_FOR_REVIEW
    decision: AdaptationReviewDecision = AdaptationReviewDecision.PENDING
    operations: tuple[AdaptationOperation, ...] = Field(min_length=1)
    verification_commands: tuple[NonEmptyText, ...] = Field(min_length=1)
    open_questions: tuple[NonEmptyText, ...] = ()
    framework_files_modified: Literal[False] = False
    generated_source_included: Literal[False] = False
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)

    @field_validator("created_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("adaptation timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_plan_graph(self) -> AdaptationPlan:
        operation_ids = [operation.id for operation in self.operations]
        if len(operation_ids) != len(set(operation_ids)):
            raise ValueError("adaptation operation ids must be unique")
        known = set(operation_ids)
        for operation in self.operations:
            unknown = sorted(set(operation.depends_on) - known)
            if unknown:
                raise ValueError(f"operation {operation.id} depends on unknown operations {unknown}")
            if operation.id in operation.depends_on:
                raise ValueError(f"operation {operation.id} must not depend on itself")

        if self.status is AdaptationPlanStatus.READY_FOR_REVIEW:
            if self.decision is not AdaptationReviewDecision.PENDING:
                raise ValueError("ready plan must keep pending decision")
        elif self.status is AdaptationPlanStatus.ACCEPTED:
            if self.decision is not AdaptationReviewDecision.ACCEPTED:
                raise ValueError("accepted plan requires accepted decision")
        elif self.decision is not AdaptationReviewDecision.REJECTED:
            raise ValueError("rejected plan requires rejected decision")

        if self.decision is AdaptationReviewDecision.PENDING:
            if self.reviewed_at is not None or self.review_reason is not None or self.review_seconds != 0.0:
                raise ValueError("pending plan must not contain review metadata")
        else:
            if self.reviewed_at is None:
                raise ValueError("reviewed plan requires reviewed_at")
            if self.decision is AdaptationReviewDecision.REJECTED and not self.review_reason:
                raise ValueError("rejected plan requires a reason")
        return self
