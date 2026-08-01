"""Strict contract for one minimized, human-reviewed browser observation."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.observation.enums import ObservationDecision, ObservedAttributeName

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
TagName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[a-z][a-z0-9-]*$"),
]


class ObservedAttribute(ContractModel):
    """One allowlisted attribute from the selected element only."""

    name: ObservedAttributeName
    value: NonEmptyText


class ElementSnapshot(ContractModel):
    """Minimized target snapshot; values, HTML, and page text are excluded."""

    tag_name: TagName
    visible: bool
    enabled: bool
    editable: bool
    attributes: tuple[ObservedAttribute, ...] = ()
    input_value_persisted: Literal[False] = False
    text_content_persisted: Literal[False] = False
    html_persisted: Literal[False] = False

    @field_validator("attributes")
    @classmethod
    def attribute_names_must_be_unique(
        cls,
        value: tuple[ObservedAttribute, ...],
    ) -> tuple[ObservedAttribute, ...]:
        names = [attribute.name for attribute in value]
        if len(names) != len(set(names)):
            raise ValueError("observed attribute names must be unique")
        return value


class LocatorVerification(ContractModel):
    """Proof that one existing context locator selected one visible target."""

    locator_id: Identifier
    strategy: LocatorStrategy
    value: NonEmptyText
    match_count: Literal[1] = 1
    visible: Literal[True] = True


class BrowserObservation(ContractModel):
    """One local, bounded browser observation and its human review state."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    context_id: Identifier
    target_element_id: Identifier
    target_locator_id: Identifier
    source_url: NonEmptyText
    captured_at: datetime
    sensitivity: SensitivityLevel
    capture_seconds: float = Field(ge=0.0)
    locator: LocatorVerification
    element: ElementSnapshot
    capture_sha256: Sha256
    raw_page_persisted: Literal[False] = False
    screenshot_persisted: Literal[False] = False
    decision: ObservationDecision = ObservationDecision.PENDING
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)

    @field_validator("captured_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_timezone_aware(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("observation timestamps must include a timezone offset")
        return value

    @field_validator("source_url")
    @classmethod
    def source_url_must_be_minimized(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"file", "http", "https"}:
            raise ValueError("source_url must use file, http, or https")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("source_url must not contain credentials")
        if parsed.query or parsed.fragment:
            raise ValueError("source_url must not contain query or fragment data")
        if parsed.scheme in {"http", "https"} and not parsed.netloc:
            raise ValueError("http source_url requires a host")
        return value

    @model_validator(mode="after")
    def validate_review_state(self) -> BrowserObservation:
        if self.locator.locator_id != self.target_locator_id:
            raise ValueError("locator verification must match target_locator_id")
        if self.decision is ObservationDecision.PENDING:
            if self.reviewed_at is not None or self.review_reason is not None:
                raise ValueError("pending observation must not contain review data")
            if self.review_seconds != 0.0:
                raise ValueError("pending observation must have zero review_seconds")
            return self
        if self.reviewed_at is None:
            raise ValueError("reviewed observation requires reviewed_at")
        if self.reviewed_at < self.captured_at:
            raise ValueError("reviewed_at must not precede captured_at")
        if self.decision is ObservationDecision.REJECTED and self.review_reason is None:
            raise ValueError("rejected observation requires a reason")
        return self

    @property
    def user_action_count(self) -> int:
        """One capture authorization plus an optional review decision."""

        return 1 if self.decision is ObservationDecision.PENDING else 2
