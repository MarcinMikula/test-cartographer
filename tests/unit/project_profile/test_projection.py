from datetime import timedelta

import pytest

from test_cartographer.context.enums import EvidenceSourceType, KnowledgeStatus
from test_cartographer.intake.rules import list_questions
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.project_profile.integration import (
    project_bootstrap_into_context,
    project_profile_reference,
)


def _minimal_context(accepted_at):
    seed = MinimalContextSeed(
        id="seed_project_reuse",
        context_id="ctx_project_reuse",
        title="Project profile reuse",
        initial_request="Automate a second catalog process",
        created_at=accepted_at,
    )
    return build_minimal_context(seed)


def test_projection_confirms_three_application_bootstrap_values(project_profile, accepted_at):
    context = _minimal_context(accepted_at)
    projected, _, projection = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    assert projected.application.name.status is KnowledgeStatus.CONFIRMED
    assert projected.application.environment.status is KnowledgeStatus.CONFIRMED
    assert projected.application.base_url.status is KnowledgeStatus.CONFIRMED
    assert projection.bootstrap_questions_asked == 0


def test_projection_removes_bootstrap_questions_from_intake(project_profile, accepted_at):
    context = _minimal_context(accepted_at)
    projected, _, _ = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    ids = {question.id for question in list_questions(projected)}
    assert "q_application_name" not in ids
    assert "q_application_environment" not in ids
    assert "q_application_base_url" not in ids


def test_projection_preserves_process_specific_questions(project_profile, accepted_at):
    context = _minimal_context(accepted_at)
    projected, _, _ = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    ids = {question.id for question in list_questions(projected)}
    assert "q_process_name" in ids
    assert "q_process_purpose" in ids
    assert "q_process_risk" in ids
    assert "q_process_role" in ids


def test_projection_does_not_change_process_object(project_profile, accepted_at):
    context = _minimal_context(accepted_at)
    projected, _, _ = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    assert projected.process == context.process


def test_projection_uses_system_evidence(project_profile, accepted_at):
    context = _minimal_context(accepted_at)
    projected, _, projection = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    evidence = next(item for item in projected.evidence if item.id == projection.evidence_id)
    assert evidence.source_type is EvidenceSourceType.SYSTEM
    assert evidence.content_sha256 == project_profile.configuration_fingerprint
    assert "project_profile:" in evidence.source_ref


def test_reference_persists_no_raw_project_values(project_profile, accepted_at):
    reference = project_profile_reference(
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    rendered = reference.model_dump_json()
    assert "Public Catalog" not in rendered
    assert "local_acceptance" not in rendered
    assert "127.0.0.1" not in rendered


def test_projection_is_idempotent_for_same_profile_and_timestamp(project_profile, accepted_at):
    context = _minimal_context(accepted_at)
    projected_at = accepted_at + timedelta(seconds=1)
    first, _, _ = project_bootstrap_into_context(
        context, project_profile, projected_at=projected_at
    )
    second, _, _ = project_bootstrap_into_context(
        first, project_profile, projected_at=projected_at
    )
    assert second == first
