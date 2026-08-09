from datetime import datetime, timezone
import pytest

from test_cartographer.context.enums import KnowledgeStatus, SensitivityLevel
from test_cartographer.project_profile.enums import AuthenticationDeclarationState, ProfileBindingState, ProjectValueSource
from test_cartographer.project_profile.models import AuthenticationDeclaration, ProjectApplicationBootstrap, ProjectDataPolicy, ProjectProfileBinding, ProjectValue
from test_cartographer.project_profile.service import create_project_profile

@pytest.fixture
def accepted_at():
    return datetime(2026, 8, 9, 12, 30, tzinfo=timezone.utc)

@pytest.fixture
def confirmed_value(accepted_at):
    def make(value: str):
        return ProjectValue(value=value, status=KnowledgeStatus.CONFIRMED, sensitivity=SensitivityLevel.INTERNAL, source=ProjectValueSource.HUMAN, reviewed_at=accepted_at)
    return make

@pytest.fixture
def current_binding(accepted_at):
    def make(profile_id: str, sha: str):
        return ProjectProfileBinding(profile_id=profile_id, profile_sha256=sha, state=ProfileBindingState.CURRENT, reviewed_at=accepted_at)
    return make

@pytest.fixture
def project_profile(accepted_at, confirmed_value, current_binding):
    return create_project_profile(
        profile_id="project_public_catalog",
        application=ProjectApplicationBootstrap(
            name=confirmed_value("Public Catalog"),
            environment=confirmed_value("local_acceptance"),
            base_url=confirmed_value("http://127.0.0.1:8765"),
        ),
        workspace_binding=current_binding("workspace_expansion_reference", "a"*64),
        guided_intake_binding=current_binding("guided_profile_public_catalog", "b"*64),
        data_policy=ProjectDataPolicy(),
        authentication=AuthenticationDeclaration(state=AuthenticationDeclarationState.NOT_REQUIRED),
        accepted_at=accepted_at,
    )
