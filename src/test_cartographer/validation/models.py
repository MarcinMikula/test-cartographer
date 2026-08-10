"""Strict external-validation evidence contracts version 0.1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.adaptation.models import Sha256
from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
    ValidationAuthenticationRequirement,
    ValidationFindingKind,
    ValidationLifecycleStage,
    ValidationOperatorDifficulty,
    ValidationResultConfidence,
    ValidationRunCompletion,
    ValidationStopCondition,
    ValidationTargetControl,
    ValidationTargetDifficulty,
    ValidationTargetFamiliarity,
    ValidationWorkflowKind,
    ValidationWorkflowReuseIntent,
)

GitCommitSha = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
RelativeEvidencePath = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$",
    ),
]


def _aware(value: datetime, label: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must include a timezone offset")
    return value


def _unique_text(values: tuple[str, ...], label: str) -> tuple[str, ...]:
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must be unique")
    return values


class ValidationTargetProfile(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    label: NonEmptyText
    target_url: NonEmptyText
    difficulty: ValidationTargetDifficulty
    control: ValidationTargetControl
    authentication: ValidationAuthenticationRequirement
    process_label: NonEmptyText
    allowed_actions: tuple[NonEmptyText, ...] = Field(min_length=1)
    prohibited_actions: tuple[NonEmptyText, ...] = ()
    cleanup_requirement: NonEmptyText | None = None
    authorization_statement: NonEmptyText
    operator_authorization_confirmed: Literal[True]
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    target_fingerprint: Sha256

    @field_validator("target_url")
    @classmethod
    def validate_target_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("validation target_url must be absolute HTTP(S)")
        if parsed.username or parsed.password:
            raise ValueError("validation target_url must not contain credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("validation target_url must not contain query or fragment")
        return value

    @field_validator("allowed_actions", "prohibited_actions")
    @classmethod
    def unique_actions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _unique_text(value, "validation target actions")


class ValidationProductReference(ContractModel):
    product: Literal["test-cartographer"] = "test-cartographer"
    git_commit: GitCommitSha
    version: NonEmptyText
    working_tree_fingerprint: Sha256 | None = None


class ValidationRuntimeEnvironment(ContractModel):
    operating_system: NonEmptyText
    python_version: NonEmptyText | None = None
    browser_name: NonEmptyText | None = None
    browser_version: NonEmptyText | None = None
    llm_provider: NonEmptyText | None = None
    llm_model: NonEmptyText | None = None


class ValidationTiming(ContractModel):
    elapsed_seconds: float = Field(ge=0)
    setup_active_seconds: float = Field(ge=0)
    intake_active_seconds: float = Field(ge=0)
    review_active_seconds: float = Field(ge=0)
    correction_active_seconds: float = Field(ge=0)
    system_wait_seconds: float = Field(ge=0)

    @property
    def operator_active_seconds(self) -> float:
        return (
            self.setup_active_seconds
            + self.intake_active_seconds
            + self.review_active_seconds
            + self.correction_active_seconds
        )


class ValidationOperatorAssessment(ContractModel):
    difficulty: ValidationOperatorDifficulty
    confidence_in_result: ValidationResultConfidence
    would_reuse_workflow: ValidationWorkflowReuseIntent
    prior_target_familiarity: ValidationTargetFamiliarity


class ValidationFinding(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    observed_at: datetime
    lifecycle_stage: ValidationLifecycleStage
    kind: ValidationFindingKind
    observation: NonEmptyText
    evidence_ids: tuple[Identifier, ...] = ()
    could_continue: bool
    stop_condition: ValidationStopCondition | None = None

    @field_validator("observed_at")
    @classmethod
    def validate_observed_at(cls, value: datetime) -> datetime:
        return _aware(value, "validation finding observed_at")

    @field_validator("evidence_ids")
    @classmethod
    def unique_evidence_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _unique_text(value, "validation finding evidence_ids")

    @model_validator(mode="after")
    def validate_stop_semantics(self) -> "ValidationFinding":
        if self.kind is ValidationFindingKind.SAFETY_STOP:
            if self.could_continue:
                raise ValueError("safety_stop finding must not allow continuation")
            if self.stop_condition is None:
                raise ValueError("safety_stop finding requires stop_condition")
        elif self.stop_condition is not None:
            raise ValueError("stop_condition is valid only for safety_stop finding")
        return self


class ValidationFindingReference(ContractModel):
    run_id: Identifier
    finding_id: Identifier


class ValidationRun(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    target_profile_id: Identifier
    target_profile_fingerprint: Sha256
    workflow: ValidationWorkflowKind
    product_ref: ValidationProductReference | None = None
    predecessor_run_id: Identifier | None = None
    addressed_findings: tuple[ValidationFindingReference, ...] = ()
    started_at: datetime
    finished_at: datetime
    runtime: ValidationRuntimeEnvironment
    timing: ValidationTiming
    findings: tuple[ValidationFinding, ...] = ()
    completion: ValidationRunCompletion
    stop_condition: ValidationStopCondition | None = None
    operator_assessment: ValidationOperatorAssessment
    run_fingerprint: Sha256

    @field_validator("started_at", "finished_at")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        return _aware(value, "validation run timestamp")

    @field_validator("addressed_findings")
    @classmethod
    def unique_addressed_findings(
        cls,
        value: tuple[ValidationFindingReference, ...],
    ) -> tuple[ValidationFindingReference, ...]:
        keys = [(item.run_id, item.finding_id) for item in value]
        if len(keys) != len(set(keys)):
            raise ValueError("addressed finding references must be unique")
        return value

    @model_validator(mode="after")
    def validate_run(self) -> "ValidationRun":
        if self.finished_at < self.started_at:
            raise ValueError("validation run finished_at must not precede started_at")

        if self.workflow is ValidationWorkflowKind.TESTCARTOGRAPHER:
            if self.product_ref is None:
                raise ValueError("testcartographer workflow requires product_ref")
        elif self.product_ref is not None:
            raise ValueError("baseline workflow must not contain TestCartographer product_ref")

        if self.predecessor_run_id == self.id:
            raise ValueError("validation run predecessor must differ from current run")
        if self.addressed_findings and self.predecessor_run_id is None:
            raise ValueError("addressed findings require predecessor_run_id")
        if self.predecessor_run_id is not None:
            for reference in self.addressed_findings:
                if reference.run_id != self.predecessor_run_id:
                    raise ValueError(
                        "addressed finding references must belong to predecessor_run_id"
                    )

        finding_ids = [finding.id for finding in self.findings]
        if len(finding_ids) != len(set(finding_ids)):
            raise ValueError("validation finding IDs must be unique within one run")
        for finding in self.findings:
            if finding.observed_at < self.started_at or finding.observed_at > self.finished_at:
                raise ValueError(
                    "validation finding observed_at must fall within run timestamps"
                )

        if self.completion is ValidationRunCompletion.STOPPED:
            if self.stop_condition is None:
                raise ValueError("stopped validation run requires stop_condition")
        elif self.stop_condition is not None:
            raise ValueError("stop_condition is valid only for stopped validation run")

        safety_findings = [
            finding
            for finding in self.findings
            if finding.kind is ValidationFindingKind.SAFETY_STOP
        ]
        if safety_findings:
            if self.completion is not ValidationRunCompletion.STOPPED:
                raise ValueError("safety_stop finding requires stopped validation run")
            if all(finding.stop_condition != self.stop_condition for finding in safety_findings):
                raise ValueError(
                    "stopped run condition must match at least one safety_stop finding"
                )
        elif self.completion is ValidationRunCompletion.STOPPED:
            raise ValueError("stopped validation run requires a safety_stop finding")
        return self


class ValidationEvidenceEntry(ContractModel):
    relative_path: RelativeEvidencePath
    sha256: Sha256
    artefact_kind: ValidationArtefactKind
    sensitivity: SensitivityLevel
    producer: ValidationArtefactProducer
    finding_ids: tuple[Identifier, ...] = ()

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        if value.startswith("/") or "\\" in value or ".." in value.split("/"):
            raise ValueError("validation evidence path must be safe and relative")
        return value

    @field_validator("finding_ids")
    @classmethod
    def unique_finding_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _unique_text(value, "validation evidence finding_ids")


class ValidationEvidenceManifest(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    target_profile_id: Identifier
    target_profile_fingerprint: Sha256
    validation_run_id: Identifier
    validation_run_fingerprint: Sha256
    entries: tuple[ValidationEvidenceEntry, ...] = Field(min_length=1)
    package_fingerprint: Sha256

    @model_validator(mode="after")
    def validate_entries(self) -> "ValidationEvidenceManifest":
        paths = [entry.relative_path for entry in self.entries]
        if len(paths) != len(set(paths)):
            raise ValueError("validation evidence paths must be unique")
        if paths != sorted(paths):
            raise ValueError("validation evidence entries must be sorted by relative_path")
        return self
