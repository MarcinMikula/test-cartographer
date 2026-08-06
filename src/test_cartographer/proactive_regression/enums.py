"""Enums for bounded proactive frontend/context regression."""

from enum import StrEnum


class AuthenticationMode(StrEnum):
    """Authentication boundary supported by the first proactive slice."""

    NONE = "none"


class InventoryReviewDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ChangeDisposition(StrEnum):
    UNCHANGED = "unchanged"
    LOCATOR_DRIFT = "locator_drift"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"


class AutomationImpact(StrEnum):
    NONE_DETECTED = "none_detected"
    CURRENT_TEST_RISK = "current_test_risk"
    MAPPED_CONTEXT_STALE = "mapped_context_stale"
    HUMAN_REVIEW_REQUIRED = "human_review_required"


class ProactiveRunStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ReportReviewDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
