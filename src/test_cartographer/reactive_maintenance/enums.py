"""Closed vocabularies for controlled reactive maintenance version 0.1."""

from enum import StrEnum


class MaintenanceDisposition(StrEnum):
    INFRASTRUCTURE_BLOCKED = "infrastructure_blocked"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REOBSERVATION_REQUIRED = "reobservation_required"
    REPAIR_CANDIDATE = "repair_candidate"


class MaintenanceStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class MaintenanceDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class MaintenanceActionKind(StrEnum):
    INITIAL_TRIGGER = "initial_trigger"
    EVIDENCE_REVIEW = "evidence_review"
    CANDIDATE_SELECTION = "candidate_selection"
    PATCH_REVIEW = "patch_review"
    EXECUTION_TRIGGER = "execution_trigger"
