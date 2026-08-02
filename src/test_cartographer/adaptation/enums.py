"""Closed vocabularies for framework inspection and adaptation planning."""

from enum import StrEnum


class RepositoryEntryKind(StrEnum):
    FILE = "file"
    DIRECTORY = "directory"


class PythonSymbolKind(StrEnum):
    CLASS = "class"
    FUNCTION = "function"


class AdaptationOperationKind(StrEnum):
    CREATE_FILE = "create_file"
    ADD_SYMBOL = "add_symbol"
    REUSE_SYMBOL = "reuse_symbol"


class AdaptationTargetKind(StrEnum):
    PAGE = "page"
    COMPONENT = "component"
    FIXTURE = "fixture"
    TEST = "test"


class AdaptationPlanStatus(StrEnum):
    READY_FOR_REVIEW = "ready_for_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class AdaptationReviewDecision(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
