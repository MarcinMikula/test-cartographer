"""Closed vocabularies for deterministic human-guided intake."""

from enum import StrEnum


class IntakeQuestionKind(StrEnum):
    """Human-answerable context targets supported in Sprint 2."""

    APPLICATION_NAME = "application_name"
    APPLICATION_ENVIRONMENT = "application_environment"
    APPLICATION_BASE_URL = "application_base_url"
    PROCESS_NAME = "process_name"
    PROCESS_PURPOSE = "process_purpose"
    PROCESS_RISK = "process_risk"
    PROCESS_ROLE = "process_role"
    PRECONDITION = "precondition"
    EXPECTED_OUTCOME = "expected_outcome"
    OPEN_QUESTION = "open_question"
    CONFLICT_RESOLUTION = "conflict_resolution"


class IntakeAnswerAction(StrEnum):
    """Deterministic actions accepted by the intake workflow."""

    PROVIDE = "provide"
    CONFIRM = "confirm"
    UNKNOWN = "unknown"
    SKIP = "skip"


class IntakeSessionState(StrEnum):
    """Lifecycle state of one persisted intake session."""

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETE = "complete"
    BLOCKED = "blocked"
