"""Deterministic constructors for accepted ProjectProfile revisions."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.project_profile.enums import ProjectProfileEventKind
from test_cartographer.project_profile.fingerprints import compute_configuration_fingerprint
from test_cartographer.project_profile.models import (
    AuthenticationDeclaration,
    ProjectApplicationBootstrap,
    ProjectDataPolicy,
    ProjectPath,
    ProjectProfile,
    ProjectProfileBinding,
    ProjectProfileEvent,
)


def create_project_profile(
    *,
    profile_id: str,
    application: ProjectApplicationBootstrap,
    workspace_binding: ProjectProfileBinding,
    guided_intake_binding: ProjectProfileBinding,
    data_policy: ProjectDataPolicy,
    authentication: AuthenticationDeclaration,
    accepted_at: datetime,
    reason_code: str = "initial_project_bootstrap",
) -> ProjectProfile:
    event = ProjectProfileEvent(
        sequence=1,
        occurred_at=accepted_at,
        kind=ProjectProfileEventKind.CREATED,
        affected_paths=(
            "application",
            "workspace_binding",
            "guided_intake_binding",
            "data_policy",
            "authentication",
        ),
        reason_code=reason_code,
        previous_revision=0,
        new_revision=1,
    )
    draft = ProjectProfile(
        id=profile_id,
        revision=1,
        created_at=accepted_at,
        updated_at=accepted_at,
        application=application,
        workspace_binding=workspace_binding,
        guided_intake_binding=guided_intake_binding,
        data_policy=data_policy,
        authentication=authentication,
        configuration_fingerprint="0" * 64,
        events=(event,),
    )
    return draft.model_copy(
        update={"configuration_fingerprint": compute_configuration_fingerprint(draft)}
    )


def revise_project_profile(
    profile: ProjectProfile,
    *,
    occurred_at: datetime,
    event_kind: ProjectProfileEventKind,
    affected_paths: tuple[ProjectPath, ...],
    reason_code: str,
    application: ProjectApplicationBootstrap | None = None,
    workspace_binding: ProjectProfileBinding | None = None,
    guided_intake_binding: ProjectProfileBinding | None = None,
    data_policy: ProjectDataPolicy | None = None,
    authentication: AuthenticationDeclaration | None = None,
) -> ProjectProfile:
    if event_kind in {ProjectProfileEventKind.CREATED, ProjectProfileEventKind.ASSESSED}:
        raise ValueError("revise_project_profile requires a mutation event kind")
    if occurred_at < profile.updated_at:
        raise ValueError("revision timestamp must not precede current updated_at")

    next_revision = profile.revision + 1
    event = ProjectProfileEvent(
        sequence=len(profile.events) + 1,
        occurred_at=occurred_at,
        kind=event_kind,
        affected_paths=affected_paths,
        reason_code=reason_code,
        previous_revision=profile.revision,
        new_revision=next_revision,
    )
    draft = profile.model_copy(
        update={
            "revision": next_revision,
            "updated_at": occurred_at,
            "application": application or profile.application,
            "workspace_binding": workspace_binding or profile.workspace_binding,
            "guided_intake_binding": guided_intake_binding or profile.guided_intake_binding,
            "data_policy": data_policy or profile.data_policy,
            "authentication": authentication or profile.authentication,
            "configuration_fingerprint": "0" * 64,
            "events": profile.events + (event,),
        }
    )
    return draft.model_copy(
        update={"configuration_fingerprint": compute_configuration_fingerprint(draft)}
    )


def append_assessment_event(
    profile: ProjectProfile,
    *,
    occurred_at: datetime,
    affected_paths: tuple[ProjectPath, ...],
    reason_code: str,
) -> ProjectProfile:
    if occurred_at < profile.updated_at:
        raise ValueError("assessment timestamp must not precede current updated_at")
    event = ProjectProfileEvent(
        sequence=len(profile.events) + 1,
        occurred_at=occurred_at,
        kind=ProjectProfileEventKind.ASSESSED,
        affected_paths=affected_paths,
        reason_code=reason_code,
        previous_revision=profile.revision,
        new_revision=profile.revision,
    )
    return profile.model_copy(update={"events": profile.events + (event,)})
