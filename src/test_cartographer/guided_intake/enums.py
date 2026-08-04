"""Closed vocabularies for live LLM-guided intake."""

from enum import StrEnum


class GuidanceProviderKind(StrEnum):
    REPLAY = "replay"
    OLLAMA = "ollama"


class GuidedIntakePhase(StrEnum):
    COLLECTION = "collection"
    REVIEW = "review"


class GuidedIntakeRunState(StrEnum):
    ACTIVE = "active"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    FAILED = "failed"


class GuidedAnswerShape(StrEnum):
    SHORT_PHRASE = "short_phrase"
    SENTENCE = "sentence"
    BULLETS = "bullets"
    CONFIRMATION = "confirmation"
