"""Strict provider-neutral contracts for bounded framework execution evidence."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.adaptation.models import PythonName, RelativePath, Sha256
from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.execution.enums import (
    ExecutionAction,
    ExecutionIssueCode,
    ExecutionOutcome,
    ExecutionPhase,
)

EnvironmentVariableName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[A-Z][A-Z0-9_]{2,79}$"),
]
VersionText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[0-9A-Za-z][0-9A-Za-z.+_-]{0,63}$"),
]

_TRACEABILITY_FIELDS = (
    "context_id",
    "process_id",
    "synthesis_run_id",
    "adaptation_plan_id",
    "code_patch_id",
)


class ExecutionEvidenceProfile(ContractModel):
    """Non-secret collection limits interpreted by the framework-side plugin."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    framework_id: Identifier
    environment_label: Identifier
    include_passed: bool = True
    max_records: int = Field(default=100, ge=1, le=1000)
    max_steps_per_test: int = Field(default=8, ge=1, le=32)
    max_failure_text_characters: int = Field(default=2000, ge=128, le=20_000)
    secret_environment_variable_names: tuple[EnvironmentVariableName, ...] = ()
    default_context_id: Identifier | None = None
    default_process_id: Identifier | None = None
    default_synthesis_run_id: Identifier | None = None
    default_adaptation_plan_id: Identifier | None = None
    default_code_patch_id: Identifier | None = None
    sensitivity: Literal[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL] = (
        SensitivityLevel.INTERNAL
    )
    input_values_persisted: Literal[False] = False
    credentials_persisted: Literal[False] = False
    raw_exception_messages_persisted: Literal[False] = False
    raw_tracebacks_persisted: Literal[False] = False
    captured_stdout_persisted: Literal[False] = False
    captured_stderr_persisted: Literal[False] = False
    html_persisted: Literal[False] = False
    screenshots_persisted: Literal[False] = False
    traces_persisted: Literal[False] = False
    live_llm_used: Literal[False] = False

    @field_validator("secret_environment_variable_names")
    @classmethod
    def secret_names_must_be_unique(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("secret environment variable names must be unique")
        return value


class SanitizedApplicationLocation(ContractModel):
    origin: NonEmptyText
    path: NonEmptyText
    credentials_persisted: Literal[False] = False
    query_persisted: Literal[False] = False
    fragment_persisted: Literal[False] = False

    @model_validator(mode="after")
    def location_must_be_minimized(self) -> SanitizedApplicationLocation:
        parsed = urlsplit(self.origin)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("application origin must be an http(s) origin")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("application origin must not contain credentials, query, or fragment")
        if parsed.path not in {"", "/"}:
            raise ValueError("application origin must not contain a path")
        if not self.path.startswith("/"):
            raise ValueError("application path must start with /")
        if "?" in self.path or "#" in self.path:
            raise ValueError("application path must not contain query or fragment")
        return self


class ExecutionStep(ContractModel):
    sequence: int = Field(ge=1)
    step_id: Identifier
    page_object: PythonName
    method_name: PythonName
    action: ExecutionAction
    target_element_id: Identifier | None = None
    locator_id: Identifier | None = None
    location: SanitizedApplicationLocation | None = None
    input_value_persisted: Literal[False] = False
    method_arguments_persisted: Literal[False] = False


class ExecutionTraceability(ContractModel):
    context_id: Identifier | None = None
    process_id: Identifier | None = None
    synthesis_run_id: Identifier | None = None
    adaptation_plan_id: Identifier | None = None
    code_patch_id: Identifier | None = None
    source_ids: tuple[Identifier, ...] = ()
    complete: bool
    missing_fields: tuple[Literal[
        "context_id",
        "process_id",
        "synthesis_run_id",
        "adaptation_plan_id",
        "code_patch_id",
    ], ...] = ()

    @field_validator("source_ids")
    @classmethod
    def source_ids_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("source traceability ids must be unique")
        return value

    @model_validator(mode="after")
    def completeness_must_match_fields(self) -> ExecutionTraceability:
        missing = tuple(
            field_name
            for field_name in _TRACEABILITY_FIELDS
            if getattr(self, field_name) is None
        )
        if tuple(self.missing_fields) != missing:
            raise ValueError("missing_fields must exactly describe absent traceability fields")
        if self.complete != (not missing):
            raise ValueError("complete must match traceability field presence")
        return self


class TestIdentity(ContractModel):
    nodeid: NonEmptyText
    relative_path: RelativePath
    test_name: PythonName
    line_number: int = Field(ge=1)
    marker_names: tuple[PythonName, ...] = ()

    @field_validator("marker_names")
    @classmethod
    def marker_names_must_be_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("marker names must be unique")
        return value


class RuntimeEnvironment(ContractModel):
    framework_id: Identifier
    environment_label: Identifier
    python_version: VersionText
    pytest_version: VersionText
    playwright_version: VersionText | None = None
    platform_system: NonEmptyText
    host_name_persisted: Literal[False] = False
    environment_values_persisted: Literal[False] = False


class FailureLocation(ContractModel):
    relative_path: RelativePath
    line_number: int = Field(ge=1)
    function_name: PythonName


class FailureSummary(ContractModel):
    phase: ExecutionPhase
    exception_type: NonEmptyText
    safe_summary: NonEmptyText
    message_sha256: Sha256
    traceback_sha256: Sha256
    redaction_count: int = Field(ge=0)
    message_truncated: bool
    location: FailureLocation | None = None
    raw_message_persisted: Literal[False] = False
    raw_traceback_persisted: Literal[False] = False
    captured_output_persisted: Literal[False] = False
    expected_actual_values_persisted: Literal[False] = False


class ExecutionEvidenceRecord(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    run_id: Identifier
    profile_id: Identifier
    captured_at: datetime
    outcome: ExecutionOutcome
    test: TestIdentity
    traceability: ExecutionTraceability
    environment: RuntimeEnvironment
    duration_seconds: float = Field(ge=0.0)
    steps: tuple[ExecutionStep, ...] = Field(default=(), max_length=32)
    failure: FailureSummary | None = None
    sensitivity: Literal[SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL]
    raw_page_persisted: Literal[False] = False
    input_values_persisted: Literal[False] = False
    credentials_persisted: Literal[False] = False
    raw_exception_messages_persisted: Literal[False] = False
    raw_tracebacks_persisted: Literal[False] = False
    captured_stdout_persisted: Literal[False] = False
    captured_stderr_persisted: Literal[False] = False
    html_persisted: Literal[False] = False
    screenshots_persisted: Literal[False] = False
    traces_persisted: Literal[False] = False
    framework_execution_independent: Literal[True] = True
    cartographer_runtime_required: Literal[False] = False
    live_llm_used: Literal[False] = False

    @field_validator("captured_at")
    @classmethod
    def timestamp_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone offset")
        return value

    @model_validator(mode="after")
    def outcome_must_match_failure(self) -> ExecutionEvidenceRecord:
        if self.outcome is ExecutionOutcome.PASSED:
            if self.failure is not None:
                raise ValueError("passed execution evidence must not contain failure details")
        elif self.failure is None:
            raise ValueError("failed execution evidence requires failure details")

        if self.outcome is ExecutionOutcome.TEST_FAILURE and self.failure is not None:
            if self.failure.phase is not ExecutionPhase.CALL:
                raise ValueError("test_failure must originate in the call phase")
        return self


class ExecutionEvidenceBundle(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    run_id: Identifier
    profile_id: Identifier
    started_at: datetime
    completed_at: datetime
    records: tuple[ExecutionEvidenceRecord, ...] = ()
    passed_count: int = Field(ge=0)
    test_failure_count: int = Field(ge=0)
    infrastructure_error_count: int = Field(ge=0)
    truncated_record_count: int = Field(default=0, ge=0)
    collector_name: Literal["test_cartographer_pytest_reference"] = (
        "test_cartographer_pytest_reference"
    )
    collector_version: Literal["0.1"] = "0.1"
    framework_execution_independent: Literal[True] = True
    cartographer_runtime_required: Literal[False] = False
    raw_artifacts_persisted: Literal[False] = False
    live_llm_used: Literal[False] = False

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("bundle timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def bundle_counts_must_match_records(self) -> ExecutionEvidenceBundle:
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not be earlier than started_at")
        ids = [record.id for record in self.records]
        if len(ids) != len(set(ids)):
            raise ValueError("execution evidence record ids must be unique")
        if any(record.run_id != self.run_id for record in self.records):
            raise ValueError("all records must belong to the bundle run")
        if any(record.profile_id != self.profile_id for record in self.records):
            raise ValueError("all records must belong to the bundle profile")
        counts = {
            ExecutionOutcome.PASSED: 0,
            ExecutionOutcome.TEST_FAILURE: 0,
            ExecutionOutcome.INFRASTRUCTURE_ERROR: 0,
        }
        for record in self.records:
            counts[record.outcome] += 1
        if self.passed_count != counts[ExecutionOutcome.PASSED]:
            raise ValueError("passed_count does not match records")
        if self.test_failure_count != counts[ExecutionOutcome.TEST_FAILURE]:
            raise ValueError("test_failure_count does not match records")
        if self.infrastructure_error_count != counts[ExecutionOutcome.INFRASTRUCTURE_ERROR]:
            raise ValueError("infrastructure_error_count does not match records")
        return self


class ExecutionEvidenceAssessment(ContractModel):
    bundle_id: Identifier
    record_count: int = Field(ge=0)
    failure_count: int = Field(ge=0)
    complete_traceability_count: int = Field(ge=0)
    actionable_failure_count: int = Field(ge=0)
    missing_traceability_count: int = Field(ge=0)
    missing_last_step_count: int = Field(ge=0)
    issue_codes: tuple[ExecutionIssueCode, ...] = ()
    ready_for_reactive_maintenance: bool
