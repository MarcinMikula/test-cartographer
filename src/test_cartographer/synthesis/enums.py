"""Closed vocabularies for bounded LLM synthesis protocol version 0.1."""

from enum import StrEnum


class SynthesisRunStatus(StrEnum):
    """Lifecycle state of one bounded synthesis run."""

    PROTOCOL_ERROR = "protocol_error"
    VALIDATION_REJECTED = "validation_rejected"
    READY_FOR_REVIEW = "ready_for_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ProposalReviewDecision(StrEnum):
    """Human decision over one validated proposal."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ProposalOwnerKind(StrEnum):
    """Logical automation object that owns a proposed method."""

    PAGE = "page"
    COMPONENT = "component"


class ValidationSeverity(StrEnum):
    """Deterministic proposal-validation severity."""

    ERROR = "error"
    WARNING = "warning"


class ExclusionReason(StrEnum):
    """Why a context field is deliberately excluded from the LLM request."""

    POLICY = "policy"
    SENSITIVITY = "sensitivity"
    STATUS = "status"
    NOT_REQUIRED = "not_required"
