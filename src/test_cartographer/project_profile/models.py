"""Strict contracts for persistent project bootstrap/profile state version 0.1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.adaptation.models import Sha256
from test_cartographer.context.enums import KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.project_profile.enums import (
    AuthenticationDeclarationState,
    ProfileBindingState,
    ProjectProfileEventKind,
    ProjectProfileIssueSeverity,
    ProjectValueSource,
)

ProjectPath = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        pattern=r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)*$",
    ),
]


def _aware(value: datetime | None, label: str) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError(f"{label} must include a timezone offset")
    return value


class ProjectValue(ContractModel):
    value: NonEmptyText | None
    status: KnowledgeStatus
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    source: ProjectValueSource
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None

    @field_validator("reviewed_at")
    @classmethod
    def validate_reviewed_at(cls, value: datetime | None) -> datetime | None:
        return _aware(value, "project value reviewed_at")

    @model_validator(mode="after")
    def validate_value(self) -> "ProjectValue":
        if self.status is KnowledgeStatus.UNKNOWN:
            if self.value is not None or self.reviewed_at is not None or self.review_reason is not None:
                raise ValueError("unknown project value must not contain value or review metadata")
            return self
        if self.status is KnowledgeStatus.CONFLICTING:
            if self.value is not None:
                raise ValueError("conflicting project value must not select one value")
            if not self.review_reason:
                raise ValueError("conflicting project value requires review_reason")
            return self
        if self.value is None:
            raise ValueError(f"{self.status.value} project value requires value")
        if self.status is KnowledgeStatus.CONFIRMED and self.reviewed_at is None:
            raise ValueError("confirmed project value requires reviewed_at")
        if self.status is KnowledgeStatus.STALE and not self.review_reason:
            raise ValueError("stale project value requires review_reason")
        return self


class ProjectApplicationBootstrap(ContractModel):
    name: ProjectValue
    environment: ProjectValue
    base_url: ProjectValue

    @model_validator(mode="after")
    def validate_base_url(self) -> "ProjectApplicationBootstrap":
        if self.base_url.value is None:
            return self
        parsed = urlparse(self.base_url.value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("project base_url must be absolute HTTP(S)")
        if parsed.username or parsed.password:
            raise ValueError("project base_url must not contain credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("project base_url must not contain query or fragment")
        return self


class ProjectProfileBinding(ContractModel):
    profile_id: Identifier | None = None
    profile_sha256: Sha256 | None = None
    state: ProfileBindingState
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None

    @field_validator("reviewed_at")
    @classmethod
    def validate_reviewed_at(cls, value: datetime | None) -> datetime | None:
        return _aware(value, "profile binding reviewed_at")

    @model_validator(mode="after")
    def validate_binding(self) -> "ProjectProfileBinding":
        has_any = self.profile_id is not None or self.profile_sha256 is not None
        if has_any and (self.profile_id is None or self.profile_sha256 is None):
            raise ValueError("profile binding id and sha256 must appear together")
        if self.state is ProfileBindingState.UNRESOLVED:
            if has_any or self.reviewed_at is not None:
                raise ValueError("unresolved binding must not contain accepted identity/review")
            return self
        if not has_any:
            raise ValueError(f"{self.state.value} binding requires profile id and sha256")
        if self.state is ProfileBindingState.CURRENT:
            if self.reviewed_at is None:
                raise ValueError("current binding requires reviewed_at")
        elif not self.review_reason:
            raise ValueError(f"{self.state.value} binding requires review_reason")
        return self


class ProjectDataPolicy(ContractModel):
    external_processing_allowed: bool = False
    allowed_context_sensitivities: tuple[SensitivityLevel, ...] = (
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
    )
    raw_application_content_persisted: Literal[False] = False
    raw_secret_values_persisted: Literal[False] = False

    @field_validator("allowed_context_sensitivities")
    @classmethod
    def validate_sensitivities(
        cls, value: tuple[SensitivityLevel, ...]
    ) -> tuple[SensitivityLevel, ...]:
        if not value:
            raise ValueError("allowed_context_sensitivities must not be empty")
        if len(value) != len(set(value)):
            raise ValueError("allowed_context_sensitivities must be unique")
        return value


class AuthenticationDeclaration(ContractModel):
    state: AuthenticationDeclarationState
    auth_profile_ref: Identifier | None = None

    @model_validator(mode="after")
    def validate_reference(self) -> "AuthenticationDeclaration":
        if self.state is AuthenticationDeclarationState.CONFIGURED_REF:
            if self.auth_profile_ref is None:
                raise ValueError("configured_ref authentication requires auth_profile_ref")
        elif self.auth_profile_ref is not None:
            raise ValueError("auth_profile_ref is valid only for configured_ref authentication")
        return self


class ProjectProfileEvent(ContractModel):
    sequence: int = Field(ge=1)
    occurred_at: datetime
    kind: ProjectProfileEventKind
    affected_paths: tuple[ProjectPath, ...] = Field(min_length=1)
    reason_code: NonEmptyText
    previous_revision: int = Field(ge=0)
    new_revision: int = Field(ge=1)

    @field_validator("occurred_at")
    @classmethod
    def validate_occurred_at(cls, value: datetime) -> datetime:
        return _aware(value, "profile event occurred_at")  # type: ignore[return-value]

    @field_validator("affected_paths")
    @classmethod
    def unique_paths(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("profile event affected_paths must be unique")
        return value

    @model_validator(mode="after")
    def validate_transition(self) -> "ProjectProfileEvent":
        if self.kind is ProjectProfileEventKind.CREATED:
            if self.previous_revision != 0 or self.new_revision != 1:
                raise ValueError("created event must transition revision 0 -> 1")
        elif self.kind is ProjectProfileEventKind.ASSESSED:
            if self.previous_revision != self.new_revision:
                raise ValueError("assessed event must not change revision")
        elif self.new_revision != self.previous_revision + 1:
            raise ValueError("profile mutation event must increment revision by one")
        return self


class ProjectProfile(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    revision: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime
    application: ProjectApplicationBootstrap
    workspace_binding: ProjectProfileBinding
    guided_intake_binding: ProjectProfileBinding
    data_policy: ProjectDataPolicy
    authentication: AuthenticationDeclaration
    configuration_fingerprint: Sha256
    events: tuple[ProjectProfileEvent, ...] = Field(min_length=1)
    secret_values_persisted: Literal[False] = False
    raw_auth_state_persisted: Literal[False] = False
    arbitrary_metadata_allowed: Literal[False] = False

    @field_validator("created_at", "updated_at")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        return _aware(value, "project profile timestamp")  # type: ignore[return-value]

    @model_validator(mode="after")
    def validate_profile(self) -> "ProjectProfile":
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not precede created_at")
        sequences = [event.sequence for event in self.events]
        if sequences != list(range(1, len(sequences) + 1)):
            raise ValueError("profile event sequence must be contiguous and start at 1")
        if self.events[0].kind is not ProjectProfileEventKind.CREATED:
            raise ValueError("profile event ledger must start with created event")
        current_revision = 0
        for event in self.events:
            if event.previous_revision != current_revision:
                raise ValueError("profile event ledger revision chain is broken")
            current_revision = event.new_revision
        if current_revision != self.revision:
            raise ValueError("profile revision must match event ledger")
        return self


class ProjectProfileReadinessIssue(ContractModel):
    code: Identifier
    severity: ProjectProfileIssueSeverity
    path: ProjectPath
    message: NonEmptyText


class ProjectProfileReadinessReport(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    profile_id: Identifier
    revision: int = Field(ge=1)
    configuration_fingerprint: Sha256
    ready_for_bootstrap_reuse: bool
    bootstrap_questions_required: int = Field(ge=0)
    workspace_binding_current: bool
    guided_intake_binding_current: bool
    authentication_declaration_resolved: bool
    issues: tuple[ProjectProfileReadinessIssue, ...] = ()


class ProjectProfileBindingValidation(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    profile_id: Identifier
    workspace_id_match: bool
    workspace_hash_match: bool
    guided_intake_id_match: bool
    guided_intake_hash_match: bool
    all_bindings_match: bool
