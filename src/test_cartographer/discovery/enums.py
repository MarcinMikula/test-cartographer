"""Closed vocabularies for guided multi-element browser discovery."""

from enum import StrEnum


class DiscoveryProviderKind(StrEnum):
    REPLAY = "replay"
    OLLAMA = "ollama"


class DiscoveryRunState(StrEnum):
    CAPTURED = "captured"
    AWAITING_RESOLUTION = "awaiting_resolution"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class DiscoveryTargetState(StrEnum):
    SELECTED = "selected"
    AMBIGUOUS = "ambiguous"
    MISSING = "missing"


class SelectionAuthority(StrEnum):
    DETERMINISTIC = "deterministic"
    HUMAN = "human"


class DiscoveryDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
