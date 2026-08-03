"""Closed vocabularies for framework execution evidence version 0.1."""

from enum import StrEnum


class ExecutionOutcome(StrEnum):
    PASSED = "passed"
    TEST_FAILURE = "test_failure"
    INFRASTRUCTURE_ERROR = "infrastructure_error"


class ExecutionPhase(StrEnum):
    COLLECTION = "collection"
    SETUP = "setup"
    CALL = "call"
    TEARDOWN = "teardown"


class ExecutionAction(StrEnum):
    NAVIGATE = "navigate"
    FILL = "fill"
    CLICK = "click"
    SELECT = "select"
    READ = "read"
    ASSERT = "assert"
    SETUP = "setup"
    OTHER = "other"


class ExecutionIssueCode(StrEnum):
    NO_FAILURE_EVIDENCE = "no_failure_evidence"
    INCOMPLETE_TRACEABILITY = "incomplete_traceability"
    MISSING_LAST_STEP = "missing_last_step"
    RECORDS_TRUNCATED = "records_truncated"
