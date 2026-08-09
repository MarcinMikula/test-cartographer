"""Readiness and binding-currentness assessment for ProjectProfile v0.1."""

from __future__ import annotations

from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.project_profile.enums import (
    AuthenticationDeclarationState,
    ProfileBindingState,
    ProjectProfileIssueSeverity,
)
from test_cartographer.project_profile.fingerprints import canonical_model_sha256
from test_cartographer.project_profile.models import (
    ProjectProfile,
    ProjectProfileBindingValidation,
    ProjectProfileReadinessIssue,
    ProjectProfileReadinessReport,
)


def assess_project_profile(profile: ProjectProfile) -> ProjectProfileReadinessReport:
    issues: list[ProjectProfileReadinessIssue] = []
    bootstrap_questions = 0

    for field_name in ("name", "environment", "base_url"):
        value = getattr(profile.application, field_name)
        if value.status is not KnowledgeStatus.CONFIRMED:
            bootstrap_questions += 1
            issues.append(
                ProjectProfileReadinessIssue(
                    code=f"{field_name}_not_confirmed",
                    severity=ProjectProfileIssueSeverity.BLOCKER,
                    path=f"application.{field_name}",
                    message=f"Project application {field_name} is not confirmed for bootstrap reuse.",
                )
            )

    workspace_current = profile.workspace_binding.state is ProfileBindingState.CURRENT
    if not workspace_current:
        issues.append(
            ProjectProfileReadinessIssue(
                code="workspace_binding_not_current",
                severity=ProjectProfileIssueSeverity.BLOCKER,
                path="workspace_binding",
                message="WorkspaceProfile binding requires resolution or review.",
            )
        )

    guided_current = profile.guided_intake_binding.state is ProfileBindingState.CURRENT
    if not guided_current:
        issues.append(
            ProjectProfileReadinessIssue(
                code="guided_binding_not_current",
                severity=ProjectProfileIssueSeverity.BLOCKER,
                path="guided_intake_binding",
                message="GuidedIntakeProfile binding requires resolution or review.",
            )
        )

    auth_resolved = (
        profile.authentication.state
        is not AuthenticationDeclarationState.REQUIRED_UNRESOLVED
    )
    if not auth_resolved:
        issues.append(
            ProjectProfileReadinessIssue(
                code="authentication_unresolved",
                severity=ProjectProfileIssueSeverity.BLOCKER,
                path="authentication",
                message="Project requires authentication but no symbolic AuthProfile reference is configured.",
            )
        )

    ready = not any(
        issue.severity is ProjectProfileIssueSeverity.BLOCKER for issue in issues
    )
    return ProjectProfileReadinessReport(
        profile_id=profile.id,
        revision=profile.revision,
        configuration_fingerprint=profile.configuration_fingerprint,
        ready_for_bootstrap_reuse=ready,
        bootstrap_questions_required=bootstrap_questions,
        workspace_binding_current=workspace_current,
        guided_intake_binding_current=guided_current,
        authentication_declaration_resolved=auth_resolved,
        issues=tuple(issues),
    )


def assess_bound_profiles(
    profile: ProjectProfile,
    *,
    workspace_profile: WorkspaceProfile,
    guided_intake_profile: GuidedIntakeProfile,
) -> ProjectProfileBindingValidation:
    workspace_id_match = profile.workspace_binding.profile_id == workspace_profile.id
    workspace_hash_match = (
        profile.workspace_binding.profile_sha256 == canonical_model_sha256(workspace_profile)
    )
    guided_id_match = profile.guided_intake_binding.profile_id == guided_intake_profile.id
    guided_hash_match = (
        profile.guided_intake_binding.profile_sha256
        == canonical_model_sha256(guided_intake_profile)
    )
    return ProjectProfileBindingValidation(
        profile_id=profile.id,
        workspace_id_match=workspace_id_match,
        workspace_hash_match=workspace_hash_match,
        guided_intake_id_match=guided_id_match,
        guided_intake_hash_match=guided_hash_match,
        all_bindings_match=all(
            (workspace_id_match, workspace_hash_match, guided_id_match, guided_hash_match)
        ),
    )
