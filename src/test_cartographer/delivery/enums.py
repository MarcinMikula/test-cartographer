"""Closed vocabularies for controlled source delivery version 0.1."""

from enum import StrEnum


class SourceChangeKind(StrEnum):
    CREATE_FILE = "create_file"
    APPEND_SYMBOL = "append_symbol"
    REPLACE_FILE = "replace_file"


class CodePatchStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PatchReviewDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PatchApplicationStatus(StrEnum):
    APPLIED = "applied"


class CreationEvaluationStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
