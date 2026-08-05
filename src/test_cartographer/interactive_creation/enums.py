"""Closed vocabularies for the human-triggered Creation Flow."""

from enum import StrEnum


class InteractiveSessionState(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ABORTED = "aborted"
    COMPLETE = "complete"


class OperatorActionKind(StrEnum):
    INITIAL_REQUEST = "initial_request"
    INTAKE_ANSWER = "intake_answer"
    INTAKE_CONFIRMATION = "intake_confirmation"
    SYNTHESIS_HANDOFF_CONFIRMATION = "synthesis_handoff_confirmation"
    AMBIGUITY_SELECTION = "ambiguity_selection"
    REVIEW_DECISION = "review_decision"
    EXECUTION_TRIGGER = "execution_trigger"
