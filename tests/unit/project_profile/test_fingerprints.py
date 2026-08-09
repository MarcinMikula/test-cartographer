from datetime import timedelta
import pytest
from test_cartographer.project_profile.enums import ProjectProfileEventKind
from test_cartographer.project_profile.fingerprints import compute_configuration_fingerprint, validate_configuration_fingerprint
from test_cartographer.project_profile.service import append_assessment_event, revise_project_profile

def test_created_profile_fingerprint_is_valid(project_profile):
    validate_configuration_fingerprint(project_profile)

def test_assessment_event_does_not_change_configuration_fingerprint(project_profile, accepted_at):
    assessed = append_assessment_event(project_profile, occurred_at=accepted_at+timedelta(seconds=1), affected_paths=("workspace_binding",), reason_code="binding_checked")
    assert assessed.configuration_fingerprint == project_profile.configuration_fingerprint
    assert compute_configuration_fingerprint(assessed) == project_profile.configuration_fingerprint

def test_accepted_revision_changes_fingerprint(project_profile, accepted_at, confirmed_value):
    app = project_profile.application.model_copy(update={"environment": confirmed_value("local_acceptance_2")})
    revised = revise_project_profile(project_profile, occurred_at=accepted_at+timedelta(seconds=2), event_kind=ProjectProfileEventKind.CHANGED, affected_paths=("application.environment",), reason_code="environment_changed", application=app)
    assert revised.revision == 2
    assert revised.configuration_fingerprint != project_profile.configuration_fingerprint

def test_tampered_fingerprint_fails(project_profile):
    tampered = project_profile.model_copy(update={"configuration_fingerprint": "f"*64})
    with pytest.raises(ValueError):
        validate_configuration_fingerprint(tampered)

def test_revision_helper_rejects_assessed_kind(project_profile, accepted_at):
    with pytest.raises(ValueError):
        revise_project_profile(project_profile, occurred_at=accepted_at+timedelta(seconds=1), event_kind=ProjectProfileEventKind.ASSESSED, affected_paths=("application",), reason_code="bad")
