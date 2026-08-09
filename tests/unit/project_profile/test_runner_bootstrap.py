from datetime import timedelta

import pytest

from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.intake.rules import list_questions
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.interactive_creation.project_profile import (
    apply_persistent_project_bootstrap,
    validate_guided_intake_binding,
    validate_workspace_binding,
)
from test_cartographer.project_profile.fingerprints import canonical_model_sha256
from test_cartographer.project_profile.io import save_project_profile


def test_real_runner_helper_loads_profile_from_disk_and_skips_bootstrap(
    project_profile, accepted_at, tmp_path
):
    path = tmp_path / "project-profile.json"
    save_project_profile(project_profile, path)
    context = build_minimal_context(
        MinimalContextSeed(
            id="seed_runner_profile",
            context_id="ctx_runner_profile",
            title="Runner profile",
            initial_request="Automate another process",
            created_at=accepted_at,
        )
    )
    projected, loaded = apply_persistent_project_bootstrap(
        context,
        project_profile_path=path,
        output_dir=tmp_path / "artifacts",
        projected_at=accepted_at + timedelta(seconds=1),
    )
    ids = {q.id for q in list_questions(projected)}
    assert loaded.id == project_profile.id
    assert "q_application_name" not in ids
    assert "q_application_environment" not in ids
    assert "q_application_base_url" not in ids
    assert "q_process_name" in ids


def test_real_runner_helper_persists_reference_and_projection(
    project_profile, accepted_at, tmp_path
):
    path = tmp_path / "project-profile.json"
    save_project_profile(project_profile, path)
    context = build_minimal_context(
        MinimalContextSeed(
            id="seed_runner_artifacts",
            context_id="ctx_runner_artifacts",
            title="Runner artifacts",
            initial_request="Automate process",
            created_at=accepted_at,
        )
    )
    apply_persistent_project_bootstrap(
        context,
        project_profile_path=path,
        output_dir=tmp_path / "artifacts",
        projected_at=accepted_at + timedelta(seconds=1),
    )
    assert (tmp_path / "artifacts/00-project-profile-reference.json").exists()
    assert (tmp_path / "artifacts/00-project-bootstrap-projection.json").exists()


def test_workspace_binding_validator_accepts_exact_profile(project_profile):
    workspace = WorkspaceProfile(
        id=project_profile.workspace_binding.profile_id,
        repository_label="Framework",
        root_marker_files=("README.md",),
        allowed_roots=("pages",),
    )
    profile = project_profile.model_copy(
        update={
            "workspace_binding": project_profile.workspace_binding.model_copy(
                update={"profile_sha256": canonical_model_sha256(workspace)}
            )
        }
    )
    validate_workspace_binding(profile, workspace)


def test_workspace_binding_validator_rejects_hash_drift(project_profile):
    workspace = WorkspaceProfile(
        id=project_profile.workspace_binding.profile_id,
        repository_label="Changed",
        root_marker_files=("README.md",),
        allowed_roots=("pages",),
    )
    with pytest.raises(ValueError, match="WorkspaceProfile binding drift"):
        validate_workspace_binding(project_profile, workspace)


def test_guided_binding_validator_accepts_exact_profile(project_profile):
    guided = GuidedIntakeProfile(
        id=project_profile.guided_intake_binding.profile_id,
        provider=GuidanceProviderKind.OLLAMA,
        model="qwen2.5-coder:7b",
        base_url="http://127.0.0.1:11434",
    )
    profile = project_profile.model_copy(
        update={
            "guided_intake_binding": project_profile.guided_intake_binding.model_copy(
                update={"profile_sha256": canonical_model_sha256(guided)}
            )
        }
    )
    validate_guided_intake_binding(profile, guided)


def test_guided_binding_validator_rejects_model_drift(project_profile):
    guided = GuidedIntakeProfile(
        id=project_profile.guided_intake_binding.profile_id,
        provider=GuidanceProviderKind.OLLAMA,
        model="different-model",
        base_url="http://127.0.0.1:11434",
    )
    with pytest.raises(ValueError, match="GuidedIntakeProfile binding drift"):
        validate_guided_intake_binding(project_profile, guided)
