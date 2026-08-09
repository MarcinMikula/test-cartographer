import pytest
from pydantic import ValidationError
from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.project_profile.enums import AuthenticationDeclarationState, ProfileBindingState, ProjectProfileEventKind, ProjectValueSource
from test_cartographer.project_profile.models import AuthenticationDeclaration, ProjectApplicationBootstrap, ProjectProfileBinding, ProjectProfileEvent, ProjectValue

def test_confirmed_project_value_requires_review_timestamp():
    with pytest.raises(ValidationError):
        ProjectValue(value="Public Catalog", status=KnowledgeStatus.CONFIRMED, source=ProjectValueSource.HUMAN)

def test_unknown_project_value_contains_no_value():
    value = ProjectValue(value=None, status=KnowledgeStatus.UNKNOWN, source=ProjectValueSource.SYSTEM)
    assert value.value is None

def test_unknown_project_value_rejects_value():
    with pytest.raises(ValidationError):
        ProjectValue(value="guess", status=KnowledgeStatus.UNKNOWN, source=ProjectValueSource.SYSTEM)

def test_conflicting_project_value_requires_reason():
    with pytest.raises(ValidationError):
        ProjectValue(value=None, status=KnowledgeStatus.CONFLICTING, source=ProjectValueSource.HUMAN)

def test_stale_project_value_requires_reason(accepted_at):
    with pytest.raises(ValidationError):
        ProjectValue(value="old", status=KnowledgeStatus.STALE, source=ProjectValueSource.HUMAN, reviewed_at=accepted_at)

def test_application_base_url_rejects_credentials(confirmed_value):
    with pytest.raises(ValidationError):
        ProjectApplicationBootstrap(name=confirmed_value("App"), environment=confirmed_value("test"), base_url=confirmed_value("https://user:pass@example.test"))

def test_application_base_url_rejects_query(confirmed_value):
    with pytest.raises(ValidationError):
        ProjectApplicationBootstrap(name=confirmed_value("App"), environment=confirmed_value("test"), base_url=confirmed_value("https://example.test?token=x"))

def test_unresolved_binding_contains_no_identity():
    binding = ProjectProfileBinding(state=ProfileBindingState.UNRESOLVED)
    assert binding.profile_id is None

def test_current_binding_requires_review_timestamp():
    with pytest.raises(ValidationError):
        ProjectProfileBinding(profile_id="workspace_profile", profile_sha256="a"*64, state=ProfileBindingState.CURRENT)

def test_binding_requires_id_and_hash_together(accepted_at):
    with pytest.raises(ValidationError):
        ProjectProfileBinding(profile_id="workspace_profile", state=ProfileBindingState.CURRENT, reviewed_at=accepted_at)

def test_configured_auth_requires_reference():
    with pytest.raises(ValidationError):
        AuthenticationDeclaration(state=AuthenticationDeclarationState.CONFIGURED_REF)

def test_not_required_auth_rejects_reference():
    with pytest.raises(ValidationError):
        AuthenticationDeclaration(state=AuthenticationDeclarationState.NOT_REQUIRED, auth_profile_ref="auth_reference")

def test_created_event_requires_zero_to_one_transition(accepted_at):
    with pytest.raises(ValidationError):
        ProjectProfileEvent(sequence=1, occurred_at=accepted_at, kind=ProjectProfileEventKind.CREATED, affected_paths=("application",), reason_code="bad", previous_revision=1, new_revision=2)

def test_assessed_event_keeps_revision(accepted_at):
    event = ProjectProfileEvent(sequence=2, occurred_at=accepted_at, kind=ProjectProfileEventKind.ASSESSED, affected_paths=("workspace_binding",), reason_code="checked", previous_revision=1, new_revision=1)
    assert event.new_revision == event.previous_revision
