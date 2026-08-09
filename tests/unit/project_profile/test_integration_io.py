from datetime import timedelta

from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.project_profile.integration import (
    assess_project_profile_compatibility,
    project_bootstrap_into_context,
)
from test_cartographer.project_profile.integration_io import (
    load_project_profile_reference,
    save_project_bootstrap_projection,
    save_project_profile_compatibility,
    save_project_profile_reference,
)


def test_reference_round_trip(project_profile, accepted_at, tmp_path):
    context = build_minimal_context(
        MinimalContextSeed(
            id="seed_io_projection",
            context_id="ctx_io_projection",
            title="IO projection",
            initial_request="Automate catalog",
            created_at=accepted_at,
        )
    )
    _, reference, projection = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    target = tmp_path / "reference.json"
    save_project_profile_reference(reference, target)
    assert load_project_profile_reference(target) == reference
    assert target.read_bytes().endswith(b"\n")


def test_projection_and_compatibility_are_persistable(project_profile, accepted_at, tmp_path):
    context = build_minimal_context(
        MinimalContextSeed(
            id="seed_io_projection_two",
            context_id="ctx_io_projection_two",
            title="IO projection two",
            initial_request="Automate another catalog process",
            created_at=accepted_at,
        )
    )
    _, reference, projection = project_bootstrap_into_context(
        context,
        project_profile,
        projected_at=accepted_at + timedelta(seconds=1),
    )
    compatibility = assess_project_profile_compatibility(project_profile, reference)
    projection_path = tmp_path / "projection.json"
    compatibility_path = tmp_path / "compatibility.json"
    save_project_bootstrap_projection(projection, projection_path)
    save_project_profile_compatibility(compatibility, compatibility_path)
    assert '"bootstrap_questions_asked": 0' in projection_path.read_text(encoding="utf-8")
    assert '"business_context_reuse_allowed": true' in compatibility_path.read_text(encoding="utf-8")
