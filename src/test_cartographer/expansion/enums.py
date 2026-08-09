
"""Closed vocabularies for incremental expansion version 0.1."""

from enum import StrEnum


class ExpansionDisposition(StrEnum):
    """What the expansion workflow should do with one subject."""

    REUSE = "reuse"
    ASK_HUMAN = "ask_human"
    OBSERVE_NEW = "observe_new"
    REOBSERVE = "reobserve"
    REVIEW = "review"
    BLOCKED = "blocked"


class ExpansionSubjectKind(StrEnum):
    APPLICATION_VALUE = "application_value"
    PAGE_VALUE = "page_value"
    ELEMENT = "element"
    PROCESS_VALUE = "process_value"
    FRAMEWORK_SNAPSHOT = "framework_snapshot"


class ExpansionReasonCode(StrEnum):
    AUTHORIZED_CURRENT_KNOWLEDGE = "authorized_current_knowledge"
    HUMAN_EXPANSION_INTENT = "human_expansion_intent"
    NEW_PROCESS_SPECIFIC_CONTEXT = "new_process_specific_context"
    TARGET_NOT_IN_BASE_CONTEXT = "target_not_in_base_context"
    PROACTIVE_LOCATOR_DRIFT = "proactive_locator_drift"
    PROACTIVE_TARGET_MISSING = "proactive_target_missing"
    PROACTIVE_TARGET_AMBIGUOUS = "proactive_target_ambiguous"
    KNOWLEDGE_REQUIRES_REVIEW = "knowledge_requires_review"
    KNOWLEDGE_REQUIRES_REOBSERVATION = "knowledge_requires_reobservation"
    KNOWLEDGE_CONFLICT = "knowledge_conflict"
    FRAMEWORK_SNAPSHOT_BOUND = "framework_snapshot_bound"


class ExpansionPlanStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ExpansionReviewDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ExpansionRunStatus(StrEnum):
    PENDING = "pending"
    PASSED = "passed"
    REJECTED = "rejected"
    BLOCKED = "blocked"
