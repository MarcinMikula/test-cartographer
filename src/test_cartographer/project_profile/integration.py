"""ProjectProfile projection and selective compatibility for downstream context reuse."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from test_cartographer.context.enums import (
    EvidenceSourceType,
    KnowledgeStatus,
    SensitivityLevel,
)
from test_cartographer.context.models import (
    ContextBundle,
    ContractModel,
    Evidence,
    Identifier,
    KnowledgeText,
    NonEmptyText,
)
from test_cartographer.project_profile.enums import ProfileBindingState
from test_cartographer.project_profile.fingerprints import (
    validate_configuration_fingerprint,
)
from test_cartographer.project_profile.models import ProjectProfile
from test_cartographer.project_profile.readiness import assess_project_profile


class ProjectCompatibilityDisposition(StrEnum):
    COMPATIBLE = "compatible"
    REVIEW_REQUIRED = "review_required"
    REOBSERVE = "reobserve"
    RESNAPSHOT = "resnapshot"
    BLOCKED = "blocked"


class ProjectProfileReference(ContractModel):
    """Non-secret immutable reference to the project configuration used by one context."""

    schema_version: str = "0.1"
    id: Identifier
    project_profile_id: Identifier
    project_profile_revision: int = Field(ge=1)
    configuration_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    application_name_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    environment_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    base_url_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    workspace_profile_id: Identifier
    workspace_profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    guided_intake_profile_id: Identifier
    guided_intake_profile_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    data_policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    authentication_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    projected_at: datetime
    secret_values_persisted: bool = False
    raw_auth_state_persisted: bool = False
    raw_project_values_persisted: bool = False

    @field_validator("projected_at")
    @classmethod
    def projected_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("project profile reference projected_at requires timezone offset")
        return value


class ProjectBootstrapProjection(ContractModel):
    schema_version: str = "0.1"
    context_id: Identifier
    reference_id: Identifier
    evidence_id: Identifier
    project_profile_id: Identifier
    project_profile_revision: int = Field(ge=1)
    configuration_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    bootstrap_question_ids_satisfied: tuple[Identifier, ...] = Field(min_length=3, max_length=3)
    bootstrap_questions_asked: int = Field(default=0, ge=0)
    projected_at: datetime

    @field_validator("projected_at")
    @classmethod
    def projected_at_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("bootstrap projection projected_at requires timezone offset")
        return value


class ProjectProfileCompatibilityReport(ContractModel):
    schema_version: str = "0.1"
    project_profile_id: Identifier
    current_revision: int = Field(ge=1)
    reference_revision: int = Field(ge=1)
    current_configuration_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    reference_configuration_fingerprint: str = Field(pattern=r"^[0-9a-f]{64}$")
    application_identity: ProjectCompatibilityDisposition
    environment_browser_evidence: ProjectCompatibilityDisposition
    business_context: ProjectCompatibilityDisposition
    workspace: ProjectCompatibilityDisposition
    guided_intake: ProjectCompatibilityDisposition
    data_policy: ProjectCompatibilityDisposition
    authentication: ProjectCompatibilityDisposition
    current_profile_ready: bool
    business_context_reuse_allowed: bool
    reobservation_required: bool
    resnapshot_required: bool
    blockers: tuple[NonEmptyText, ...] = ()
    reasons: tuple[NonEmptyText, ...] = ()

    @model_validator(mode="after")
    def validate_report(self) -> "ProjectProfileCompatibilityReport":
        if self.blockers and self.business_context_reuse_allowed:
            raise ValueError("blocked compatibility report cannot allow business-context reuse")
        if self.environment_browser_evidence is ProjectCompatibilityDisposition.REOBSERVE:
            if not self.reobservation_required:
                raise ValueError("REOBSERVE disposition requires reobservation_required")
        if self.workspace is ProjectCompatibilityDisposition.RESNAPSHOT:
            if not self.resnapshot_required:
                raise ValueError("RESNAPSHOT disposition requires resnapshot_required")
        return self


_BOOTSTRAP_IDS = (
    "q_application_name",
    "q_application_environment",
    "q_application_base_url",
)

_SENSITIVITY_RANK = {
    SensitivityLevel.PUBLIC: 0,
    SensitivityLevel.INTERNAL: 1,
    SensitivityLevel.CONFIDENTIAL: 2,
    SensitivityLevel.RESTRICTED: 3,
}


def project_profile_reference(
    profile: ProjectProfile,
    *,
    projected_at: datetime,
) -> ProjectProfileReference:
    validate_configuration_fingerprint(profile)
    if not assess_project_profile(profile).ready_for_bootstrap_reuse:
        raise ValueError("ProjectProfile is not ready for bootstrap reuse")
    if profile.workspace_binding.profile_id is None or profile.workspace_binding.profile_sha256 is None:
        raise ValueError("current ProjectProfile requires resolved WorkspaceProfile binding")
    if profile.guided_intake_binding.profile_id is None or profile.guided_intake_binding.profile_sha256 is None:
        raise ValueError("current ProjectProfile requires resolved GuidedIntakeProfile binding")
    if projected_at.tzinfo is None or projected_at.utcoffset() is None:
        raise ValueError("projected_at must include timezone offset")
    return ProjectProfileReference(
        id=_reference_id(profile),
        project_profile_id=profile.id,
        project_profile_revision=profile.revision,
        configuration_fingerprint=profile.configuration_fingerprint,
        application_name_sha256=_project_value_sha(profile.application.name),
        environment_sha256=_project_value_sha(profile.application.environment),
        base_url_sha256=_project_value_sha(profile.application.base_url),
        workspace_profile_id=profile.workspace_binding.profile_id,
        workspace_profile_sha256=profile.workspace_binding.profile_sha256,
        guided_intake_profile_id=profile.guided_intake_binding.profile_id,
        guided_intake_profile_sha256=profile.guided_intake_binding.profile_sha256,
        data_policy_sha256=_sha_payload(
            profile.data_policy.model_dump(mode="json", exclude_none=False)
        ),
        authentication_sha256=_sha_payload(
            profile.authentication.model_dump(mode="json", exclude_none=False)
        ),
        projected_at=projected_at,
    )


def project_bootstrap_into_context(
    context: ContextBundle,
    profile: ProjectProfile,
    *,
    projected_at: datetime,
) -> tuple[ContextBundle, ProjectProfileReference, ProjectBootstrapProjection]:
    """Project current accepted bootstrap into one ContextBundle without process mutation."""

    reference = project_profile_reference(profile, projected_at=projected_at)
    evidence_id = f"ev_project_{profile.configuration_fingerprint[:16]}"
    evidence = Evidence(
        id=evidence_id,
        source_type=EvidenceSourceType.SYSTEM,
        source_ref=(
            f"project_profile:{profile.id}@{profile.revision}"
            f"#{profile.configuration_fingerprint}"
        ),
        summary=(
            "Accepted project bootstrap projected from persistent ProjectProfile "
            f"revision {profile.revision}."
        ),
        captured_at=projected_at,
        sensitivity=max(
            (
                profile.application.name.sensitivity,
                profile.application.environment.sensitivity,
                profile.application.base_url.sensitivity,
            ),
            key=lambda item: _SENSITIVITY_RANK[item],
        ),
        content_sha256=profile.configuration_fingerprint,
    )

    by_id = {item.id: item for item in context.evidence}
    existing = by_id.get(evidence.id)
    if existing is not None and existing != evidence:
        raise ValueError("project bootstrap evidence id collides with different evidence")
    by_id[evidence.id] = evidence

    def projected(project_value) -> KnowledgeText:
        if project_value.value is None:
            raise ValueError("ready ProjectProfile bootstrap value unexpectedly lacks value")
        return KnowledgeText(
            value=project_value.value,
            status=KnowledgeStatus.CONFIRMED,
            evidence_ids=(evidence.id,),
            sensitivity=project_value.sensitivity,
            notes=(
                f"Projected from ProjectProfile {profile.id} revision "
                f"{profile.revision}; do not re-ask while compatible."
            ),
        )

    application = context.application.model_copy(
        update={
            "name": projected(profile.application.name),
            "environment": projected(profile.application.environment),
            "base_url": projected(profile.application.base_url),
        }
    )
    updated = context.model_copy(
        update={
            "application": application,
            "evidence": tuple(by_id[key] for key in sorted(by_id)),
            "updated_at": max(context.updated_at, projected_at),
        }
    )
    projection = ProjectBootstrapProjection(
        context_id=context.id,
        reference_id=reference.id,
        evidence_id=evidence.id,
        project_profile_id=profile.id,
        project_profile_revision=profile.revision,
        configuration_fingerprint=profile.configuration_fingerprint,
        bootstrap_question_ids_satisfied=_BOOTSTRAP_IDS,
        bootstrap_questions_asked=0,
        projected_at=projected_at,
    )
    return updated, reference, projection


def assess_project_profile_compatibility(
    current: ProjectProfile,
    reference: ProjectProfileReference,
) -> ProjectProfileCompatibilityReport:
    """Assess future reuse without mutating current profile or historical context."""

    validate_configuration_fingerprint(current)
    readiness = assess_project_profile(current)
    blockers: list[str] = []
    reasons: list[str] = []

    if current.id != reference.project_profile_id:
        blockers.append("The context belongs to a different ProjectProfile.")
        return ProjectProfileCompatibilityReport(
            project_profile_id=current.id,
            current_revision=current.revision,
            reference_revision=reference.project_profile_revision,
            current_configuration_fingerprint=current.configuration_fingerprint,
            reference_configuration_fingerprint=reference.configuration_fingerprint,
            application_identity=ProjectCompatibilityDisposition.BLOCKED,
            environment_browser_evidence=ProjectCompatibilityDisposition.BLOCKED,
            business_context=ProjectCompatibilityDisposition.BLOCKED,
            workspace=ProjectCompatibilityDisposition.BLOCKED,
            guided_intake=ProjectCompatibilityDisposition.BLOCKED,
            data_policy=ProjectCompatibilityDisposition.BLOCKED,
            authentication=ProjectCompatibilityDisposition.BLOCKED,
            current_profile_ready=readiness.ready_for_bootstrap_reuse,
            business_context_reuse_allowed=False,
            reobservation_required=False,
            resnapshot_required=False,
            blockers=tuple(blockers),
            reasons=("ProjectProfile identity mismatch.",),
        )

    if not readiness.ready_for_bootstrap_reuse:
        blockers.append("Current ProjectProfile is not ready for bootstrap reuse.")

    app_name_changed = _project_value_sha(current.application.name) != reference.application_name_sha256
    env_changed = _project_value_sha(current.application.environment) != reference.environment_sha256
    base_url_changed = _project_value_sha(current.application.base_url) != reference.base_url_sha256
    workspace_changed = (
        current.workspace_binding.profile_id != reference.workspace_profile_id
        or current.workspace_binding.profile_sha256 != reference.workspace_profile_sha256
        or current.workspace_binding.state is not ProfileBindingState.CURRENT
    )
    guided_changed = (
        current.guided_intake_binding.profile_id != reference.guided_intake_profile_id
        or current.guided_intake_binding.profile_sha256 != reference.guided_intake_profile_sha256
        or current.guided_intake_binding.state is not ProfileBindingState.CURRENT
    )
    policy_changed = _sha_payload(
        current.data_policy.model_dump(mode="json", exclude_none=False)
    ) != reference.data_policy_sha256
    auth_changed = _sha_payload(
        current.authentication.model_dump(mode="json", exclude_none=False)
    ) != reference.authentication_sha256

    application_identity = (
        ProjectCompatibilityDisposition.REVIEW_REQUIRED
        if app_name_changed
        else ProjectCompatibilityDisposition.COMPATIBLE
    )
    if app_name_changed:
        reasons.append("Application name changed; identity label requires review.")

    environment_disposition = ProjectCompatibilityDisposition.COMPATIBLE
    if env_changed or base_url_changed:
        environment_disposition = ProjectCompatibilityDisposition.REOBSERVE
        reasons.append(
            "Environment/base URL changed; environment-bound browser evidence requires re-observation."
        )

    workspace_disposition = (
        ProjectCompatibilityDisposition.RESNAPSHOT
        if workspace_changed
        else ProjectCompatibilityDisposition.COMPATIBLE
    )
    if workspace_changed:
        reasons.append("WorkspaceProfile binding changed; repository work requires a fresh snapshot.")

    guided_disposition = (
        ProjectCompatibilityDisposition.REVIEW_REQUIRED
        if guided_changed
        else ProjectCompatibilityDisposition.COMPATIBLE
    )
    if guided_changed:
        reasons.append(
            "GuidedIntakeProfile binding changed; future guided calls use the new accepted binding."
        )

    policy_disposition = (
        ProjectCompatibilityDisposition.REVIEW_REQUIRED
        if policy_changed
        else ProjectCompatibilityDisposition.COMPATIBLE
    )
    if policy_changed:
        reasons.append("Project data policy changed; future external-processing authorization requires review.")

    auth_disposition = (
        ProjectCompatibilityDisposition.REVIEW_REQUIRED
        if auth_changed
        else ProjectCompatibilityDisposition.COMPATIBLE
    )
    if auth_changed:
        reasons.append("Authentication declaration changed; credentialed runtime assumptions require review.")

    business_context = (
        ProjectCompatibilityDisposition.BLOCKED
        if blockers
        else ProjectCompatibilityDisposition.COMPATIBLE
    )
    return ProjectProfileCompatibilityReport(
        project_profile_id=current.id,
        current_revision=current.revision,
        reference_revision=reference.project_profile_revision,
        current_configuration_fingerprint=current.configuration_fingerprint,
        reference_configuration_fingerprint=reference.configuration_fingerprint,
        application_identity=application_identity,
        environment_browser_evidence=environment_disposition,
        business_context=business_context,
        workspace=workspace_disposition,
        guided_intake=guided_disposition,
        data_policy=policy_disposition,
        authentication=auth_disposition,
        current_profile_ready=readiness.ready_for_bootstrap_reuse,
        business_context_reuse_allowed=not blockers,
        reobservation_required=environment_disposition is ProjectCompatibilityDisposition.REOBSERVE,
        resnapshot_required=workspace_disposition is ProjectCompatibilityDisposition.RESNAPSHOT,
        blockers=tuple(blockers),
        reasons=tuple(reasons),
    )


def _reference_id(profile: ProjectProfile) -> str:
    return f"project_ref_{profile.configuration_fingerprint[:16]}"


def _project_value_sha(value) -> str:
    return _sha_payload(value.model_dump(mode="json", exclude_none=False))


def _sha_payload(payload: object) -> str:
    rendered = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()
