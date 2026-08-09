from datetime import timedelta

import pytest

from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.project_profile.enums import (
    ProfileBindingState,
    ProjectProfileEventKind,
    ProjectValueSource,
)
from test_cartographer.project_profile.integration import (
    ProjectCompatibilityDisposition,
    assess_project_profile_compatibility,
    project_profile_reference,
)
from test_cartographer.project_profile.models import ProjectProfileBinding, ProjectValue
from test_cartographer.project_profile.service import (
    create_project_profile,
    revise_project_profile,
)


def _reference(profile, accepted_at):
    return project_profile_reference(
        profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )


def test_same_configuration_is_fully_compatible(project_profile, accepted_at):
    report = assess_project_profile_compatibility(
        project_profile, _reference(project_profile, accepted_at)
    )
    assert report.business_context_reuse_allowed is True
    assert report.reobservation_required is False
    assert report.resnapshot_required is False
    assert (
        report.environment_browser_evidence
        is ProjectCompatibilityDisposition.COMPATIBLE
    )


def test_time_alone_does_not_make_reference_stale(project_profile, accepted_at):
    reference = project_profile_reference(
        project_profile,
        projected_at=accepted_at - timedelta(days=365),
    )
    report = assess_project_profile_compatibility(project_profile, reference)
    assert report.business_context_reuse_allowed is True
    assert report.reobservation_required is False


def test_environment_change_requires_reobservation_but_keeps_business_context(
    project_profile, accepted_at
):
    reference = _reference(project_profile, accepted_at)
    changed_value = ProjectValue(
        value="local_acceptance_2",
        status=KnowledgeStatus.CONFIRMED,
        source=ProjectValueSource.HUMAN,
        reviewed_at=accepted_at + timedelta(seconds=2),
    )
    application = project_profile.application.model_copy(
        update={"environment": changed_value}
    )
    revised = revise_project_profile(
        project_profile,
        occurred_at=accepted_at + timedelta(seconds=2),
        event_kind=ProjectProfileEventKind.CHANGED,
        affected_paths=("application.environment",),
        reason_code="environment_changed",
        application=application,
    )
    report = assess_project_profile_compatibility(revised, reference)
    assert (
        report.environment_browser_evidence
        is ProjectCompatibilityDisposition.REOBSERVE
    )
    assert report.business_context is ProjectCompatibilityDisposition.COMPATIBLE
    assert report.business_context_reuse_allowed is True
    assert report.reobservation_required is True


def test_base_url_change_requires_reobservation(project_profile, accepted_at):
    reference = _reference(project_profile, accepted_at)
    changed_value = ProjectValue(
        value="http://127.0.0.1:9999",
        status=KnowledgeStatus.CONFIRMED,
        source=ProjectValueSource.HUMAN,
        reviewed_at=accepted_at + timedelta(seconds=2),
    )
    application = project_profile.application.model_copy(
        update={"base_url": changed_value}
    )
    revised = revise_project_profile(
        project_profile,
        occurred_at=accepted_at + timedelta(seconds=2),
        event_kind=ProjectProfileEventKind.CHANGED,
        affected_paths=("application.base_url",),
        reason_code="base_url_changed",
        application=application,
    )
    assert assess_project_profile_compatibility(
        revised, reference
    ).reobservation_required is True


def test_application_name_change_requires_identity_review_only(
    project_profile, accepted_at
):
    reference = _reference(project_profile, accepted_at)
    changed_value = ProjectValue(
        value="Renamed Catalog",
        status=KnowledgeStatus.CONFIRMED,
        source=ProjectValueSource.HUMAN,
        reviewed_at=accepted_at + timedelta(seconds=2),
    )
    revised = revise_project_profile(
        project_profile,
        occurred_at=accepted_at + timedelta(seconds=2),
        event_kind=ProjectProfileEventKind.CHANGED,
        affected_paths=("application.name",),
        reason_code="application_renamed",
        application=project_profile.application.model_copy(
            update={"name": changed_value}
        ),
    )
    report = assess_project_profile_compatibility(revised, reference)
    assert (
        report.application_identity
        is ProjectCompatibilityDisposition.REVIEW_REQUIRED
    )
    assert report.reobservation_required is False
    assert report.business_context_reuse_allowed is True


def test_workspace_binding_change_requires_resnapshot_not_business_reintake(
    project_profile, accepted_at
):
    reference = _reference(project_profile, accepted_at)
    binding = ProjectProfileBinding(
        profile_id=project_profile.workspace_binding.profile_id,
        profile_sha256="c" * 64,
        state=ProfileBindingState.CURRENT,
        reviewed_at=accepted_at + timedelta(seconds=2),
    )
    revised = revise_project_profile(
        project_profile,
        occurred_at=accepted_at + timedelta(seconds=2),
        event_kind=ProjectProfileEventKind.BINDING_CHANGED,
        affected_paths=("workspace_binding",),
        reason_code="workspace_profile_changed",
        workspace_binding=binding,
    )
    report = assess_project_profile_compatibility(revised, reference)
    assert report.workspace is ProjectCompatibilityDisposition.RESNAPSHOT
    assert report.resnapshot_required is True
    assert report.business_context_reuse_allowed is True


def test_guided_binding_change_requires_review_not_business_reintake(
    project_profile, accepted_at
):
    reference = _reference(project_profile, accepted_at)
    binding = ProjectProfileBinding(
        profile_id=project_profile.guided_intake_binding.profile_id,
        profile_sha256="d" * 64,
        state=ProfileBindingState.CURRENT,
        reviewed_at=accepted_at + timedelta(seconds=2),
    )
    revised = revise_project_profile(
        project_profile,
        occurred_at=accepted_at + timedelta(seconds=2),
        event_kind=ProjectProfileEventKind.BINDING_CHANGED,
        affected_paths=("guided_intake_binding",),
        reason_code="guided_profile_changed",
        guided_intake_binding=binding,
    )
    report = assess_project_profile_compatibility(revised, reference)
    assert (
        report.guided_intake
        is ProjectCompatibilityDisposition.REVIEW_REQUIRED
    )
    assert report.business_context is ProjectCompatibilityDisposition.COMPATIBLE


def test_unready_current_profile_blocks_historical_business_reuse(
    project_profile, accepted_at
):
    reference = _reference(project_profile, accepted_at)
    binding = ProjectProfileBinding(
        profile_id=project_profile.workspace_binding.profile_id,
        profile_sha256=project_profile.workspace_binding.profile_sha256,
        state=ProfileBindingState.REVIEW_REQUIRED,
        reviewed_at=accepted_at + timedelta(seconds=2),
        review_reason="hash mismatch requires operator review",
    )
    current = revise_project_profile(
        project_profile,
        occurred_at=accepted_at + timedelta(seconds=2),
        event_kind=ProjectProfileEventKind.INVALIDATED,
        affected_paths=("workspace_binding",),
        reason_code="workspace_binding_invalidated",
        workspace_binding=binding,
    )
    report = assess_project_profile_compatibility(current, reference)
    assert report.current_profile_ready is False
    assert report.business_context_reuse_allowed is False
    assert report.blockers


def test_different_profile_identity_blocks_reuse(project_profile, accepted_at):
    reference = _reference(project_profile, accepted_at)
    other = create_project_profile(
        profile_id="project_other_catalog",
        application=project_profile.application,
        workspace_binding=project_profile.workspace_binding,
        guided_intake_binding=project_profile.guided_intake_binding,
        data_policy=project_profile.data_policy,
        authentication=project_profile.authentication,
        accepted_at=accepted_at + timedelta(seconds=2),
        reason_code="separate_project_bootstrap",
    )
    report = assess_project_profile_compatibility(other, reference)
    assert report.business_context is ProjectCompatibilityDisposition.BLOCKED
    assert report.business_context_reuse_allowed is False


def test_tampered_current_profile_is_rejected_before_compatibility_classification(
    project_profile, accepted_at
):
    reference = _reference(project_profile, accepted_at)
    tampered = project_profile.model_copy(
        update={"id": "project_tampered_without_fingerprint_update"}
    )
    with pytest.raises(ValueError, match="configuration_fingerprint mismatch"):
        assess_project_profile_compatibility(tampered, reference)
