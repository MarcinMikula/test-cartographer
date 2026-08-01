"""Closed vocabularies used by context contract version 0.1."""

from enum import StrEnum


class KnowledgeStatus(StrEnum):
    """How a knowledge value is currently supported."""

    OBSERVED = "observed"
    PROVIDED = "provided"
    INFERRED = "inferred"
    CONFIRMED = "confirmed"
    UNKNOWN = "unknown"
    STALE = "stale"
    CONFLICTING = "conflicting"


class EvidenceSourceType(StrEnum):
    """Origin of evidence retained by the local context model."""

    HUMAN = "human"
    DOCUMENT = "document"
    APPLICATION = "application"
    REPOSITORY = "repository"
    EXECUTION = "execution"
    SYSTEM = "system"


class SensitivityLevel(StrEnum):
    """Minimum local classification used before any external LLM request."""

    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class LocatorStrategy(StrEnum):
    """Supported locator candidate types in the first contract."""

    ROLE = "role"
    LABEL = "label"
    TEST_ID = "test_id"
    PLACEHOLDER = "placeholder"
    TEXT = "text"
    CSS = "css"
    XPATH = "xpath"


class ActionKind(StrEnum):
    """Small UI-action vocabulary for one guided process."""

    NAVIGATE = "navigate"
    FILL = "fill"
    CLICK = "click"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    READ = "read"


class ReadinessSeverity(StrEnum):
    """Impact of a readiness issue on framework adaptation."""

    BLOCKER = "blocker"
    WARNING = "warning"
