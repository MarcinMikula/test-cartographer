"""ProjectProfile bootstrap reuse boundary shared by the real interactive runner."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.context.models import ContextBundle
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.project_profile.fingerprints import canonical_model_sha256
from test_cartographer.project_profile.integration import project_bootstrap_into_context
from test_cartographer.project_profile.integration_io import (
    save_project_bootstrap_projection,
    save_project_profile_reference,
)
from test_cartographer.project_profile.io import load_project_profile
from test_cartographer.project_profile.models import ProjectProfile


def load_runtime_project_profile(
    project_profile_path: str | Path,
    *,
    workspace_profile: WorkspaceProfile,
    guided_profile: GuidedIntakeProfile,
) -> ProjectProfile:
    """Load one profile and fail closed if runtime bindings drifted."""

    profile = load_project_profile(project_profile_path)
    validate_workspace_binding(profile, workspace_profile)
    validate_guided_intake_binding(profile, guided_profile)
    return profile


def apply_persistent_project_bootstrap(
    context: ContextBundle,
    *,
    project_profile_path: str | Path,
    output_dir: str | Path,
    projected_at: datetime,
    project_profile: ProjectProfile | None = None,
) -> tuple[ContextBundle, ProjectProfile]:
    """Project a disk-backed accepted bootstrap through the normal ContextBundle."""

    profile = project_profile or load_project_profile(project_profile_path)
    projected, reference, projection = project_bootstrap_into_context(
        context,
        profile,
        projected_at=projected_at,
    )
    output = Path(output_dir)
    save_project_profile_reference(
        reference,
        output / "00-project-profile-reference.json",
    )
    save_project_bootstrap_projection(
        projection,
        output / "00-project-bootstrap-projection.json",
    )
    return projected, profile


def validate_guided_intake_binding(
    profile: ProjectProfile,
    guided_profile: GuidedIntakeProfile,
) -> None:
    expected_id = profile.guided_intake_binding.profile_id
    expected_hash = profile.guided_intake_binding.profile_sha256
    actual_hash = canonical_model_sha256(guided_profile)
    if expected_id != guided_profile.id or expected_hash != actual_hash:
        raise ValueError(
            "GuidedIntakeProfile binding drift: ProjectProfile requires explicit "
            "review before guided intake can continue."
        )


def validate_workspace_binding(
    profile: ProjectProfile,
    workspace_profile: WorkspaceProfile,
) -> None:
    expected_id = profile.workspace_binding.profile_id
    expected_hash = profile.workspace_binding.profile_sha256
    actual_hash = canonical_model_sha256(workspace_profile)
    if expected_id != workspace_profile.id or expected_hash != actual_hash:
        raise ValueError(
            "WorkspaceProfile binding drift: ProjectProfile requires explicit "
            "review before repository adaptation can continue."
        )
