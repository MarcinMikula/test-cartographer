"""Closed vocabularies for persistent project-profile contract version 0.1."""

from enum import StrEnum


class ProjectValueSource(StrEnum):
    HUMAN = "human"
    SYSTEM = "system"
    MIGRATION = "migration"


class ProfileBindingState(StrEnum):
    UNRESOLVED = "unresolved"
    CURRENT = "current"
    REVIEW_REQUIRED = "review_required"
    STALE = "stale"
    CONFLICTING = "conflicting"


class AuthenticationDeclarationState(StrEnum):
    NOT_REQUIRED = "not_required"
    REQUIRED_UNRESOLVED = "required_unresolved"
    CONFIGURED_REF = "configured_ref"


class ProjectProfileEventKind(StrEnum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    CHANGED = "changed"
    INVALIDATED = "invalidated"
    REVALIDATED = "revalidated"
    BINDING_CHANGED = "binding_changed"
    ASSESSED = "assessed"


class ProjectProfileIssueSeverity(StrEnum):
    BLOCKER = "blocker"
    WARNING = "warning"
