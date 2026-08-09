from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.project_profile.enums import AuthenticationDeclarationState, ProfileBindingState, ProjectValueSource
from test_cartographer.project_profile.fingerprints import canonical_model_sha256
from test_cartographer.project_profile.models import AuthenticationDeclaration, ProjectProfileBinding, ProjectValue
from test_cartographer.project_profile.readiness import assess_bound_profiles, assess_project_profile

def test_ready_profile_requires_zero_bootstrap_questions(project_profile):
    report = assess_project_profile(project_profile)
    assert report.ready_for_bootstrap_reuse is True
    assert report.bootstrap_questions_required == 0

def test_unconfirmed_environment_requires_one_bootstrap_question(project_profile):
    provided = ProjectValue(value="local_acceptance", status=KnowledgeStatus.PROVIDED, source=ProjectValueSource.HUMAN)
    changed = project_profile.model_copy(update={"application": project_profile.application.model_copy(update={"environment": provided})})
    report = assess_project_profile(changed)
    assert report.ready_for_bootstrap_reuse is False
    assert report.bootstrap_questions_required == 1

def test_workspace_binding_not_current_blocks_reuse(project_profile, accepted_at):
    binding = ProjectProfileBinding(profile_id=project_profile.workspace_binding.profile_id, profile_sha256=project_profile.workspace_binding.profile_sha256, state=ProfileBindingState.REVIEW_REQUIRED, reviewed_at=accepted_at, review_reason="profile hash changed")
    changed = project_profile.model_copy(update={"workspace_binding": binding})
    assert assess_project_profile(changed).ready_for_bootstrap_reuse is False

def test_required_unresolved_auth_blocks_profile_reuse(project_profile):
    changed = project_profile.model_copy(update={"authentication": AuthenticationDeclaration(state=AuthenticationDeclarationState.REQUIRED_UNRESOLVED)})
    assert assess_project_profile(changed).authentication_declaration_resolved is False

def test_configured_auth_reference_is_profile_resolved(project_profile):
    changed = project_profile.model_copy(update={"authentication": AuthenticationDeclaration(state=AuthenticationDeclarationState.CONFIGURED_REF, auth_profile_ref="auth_future_profile")})
    assert assess_project_profile(changed).authentication_declaration_resolved is True

def test_bound_profiles_match_when_ids_and_hashes_match(project_profile):
    workspace = WorkspaceProfile(id="workspace_expansion_reference", repository_label="Framework", root_marker_files=("README.md",), allowed_roots=("pages","tests/e2e"))
    guided = GuidedIntakeProfile(id="guided_profile_public_catalog", provider=GuidanceProviderKind.OLLAMA, model="qwen2.5-coder:7b", base_url="http://127.0.0.1:11434")
    profile = project_profile.model_copy(update={
        "workspace_binding": project_profile.workspace_binding.model_copy(update={"profile_sha256": canonical_model_sha256(workspace)}),
        "guided_intake_binding": project_profile.guided_intake_binding.model_copy(update={"profile_sha256": canonical_model_sha256(guided)}),
    })
    assert assess_bound_profiles(profile, workspace_profile=workspace, guided_intake_profile=guided).all_bindings_match is True

def test_bound_profile_hash_drift_is_detected(project_profile):
    workspace = WorkspaceProfile(id="workspace_expansion_reference", repository_label="Changed Framework", root_marker_files=("README.md",), allowed_roots=("pages",))
    guided = GuidedIntakeProfile(id="guided_profile_public_catalog", provider=GuidanceProviderKind.OLLAMA, model="qwen2.5-coder:7b", base_url="http://127.0.0.1:11434")
    validation = assess_bound_profiles(project_profile, workspace_profile=workspace, guided_intake_profile=guided)
    assert validation.workspace_hash_match is False
    assert validation.all_bindings_match is False
