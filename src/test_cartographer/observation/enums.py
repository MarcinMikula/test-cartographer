"""Closed vocabularies for bounded browser observation version 0.1."""

from enum import StrEnum


class ObservationDecision(StrEnum):
    """Human review state for one captured browser observation."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ObservedAttributeName(StrEnum):
    """Allowlisted DOM attributes that may be persisted for a selected target."""

    ID = "id"
    ROLE = "role"
    ARIA_LABEL = "aria-label"
    NAME = "name"
    PLACEHOLDER = "placeholder"
    TYPE = "type"
    TEST_ID = "data-testid"
