from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.observation.enums import ObservationDecision, ObservedAttributeName
from test_cartographer.observation.models import (
    BrowserObservation,
    ElementSnapshot,
    LocatorVerification,
    ObservedAttribute,
)
from test_cartographer.observation.review import review_observation

CAPTURED = datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc)


def _observation() -> BrowserObservation:
    return BrowserObservation(
        id="obs_search_submit",
        context_id="ctx_public_catalog_search_observation_ready",
        target_element_id="el_search_submit",
        target_locator_id="loc_search_submit_role",
        source_url="https://catalog.example.test/catalog",
        captured_at=CAPTURED,
        sensitivity=SensitivityLevel.PUBLIC,
        capture_seconds=0.4,
        locator=LocatorVerification(
            locator_id="loc_search_submit_role",
            strategy=LocatorStrategy.ROLE,
            value="button:Search",
        ),
        element=ElementSnapshot(
            tag_name="button",
            visible=True,
            enabled=True,
            editable=False,
            attributes=(
                ObservedAttribute(
                    name=ObservedAttributeName.TYPE,
                    value="submit",
                ),
            ),
        ),
        capture_sha256="a" * 64,
    )


def test_pending_observation_has_one_user_action_and_no_raw_capture() -> None:
    observation = _observation()

    assert observation.decision is ObservationDecision.PENDING
    assert observation.user_action_count == 1
    assert observation.raw_page_persisted is False
    assert observation.screenshot_persisted is False
    assert observation.element.input_value_persisted is False
    assert observation.element.text_content_persisted is False
    assert observation.element.html_persisted is False


def test_acceptance_records_second_user_action() -> None:
    reviewed = review_observation(
        _observation(),
        decision=ObservationDecision.ACCEPTED,
        reviewed_at=CAPTURED + timedelta(seconds=2),
        reason="The target and locator mapping are correct.",
        review_seconds=0.8,
    )

    assert reviewed.decision is ObservationDecision.ACCEPTED
    assert reviewed.user_action_count == 2
    assert reviewed.review_seconds == 0.8


def test_rejection_requires_reason() -> None:
    with pytest.raises(ValidationError, match="requires a reason"):
        review_observation(
            _observation(),
            decision=ObservationDecision.REJECTED,
            reviewed_at=CAPTURED + timedelta(seconds=1),
        )


def test_source_url_rejects_query_fragment_and_credentials() -> None:
    payload = _observation().model_dump(mode="python")
    for unsafe in (
        "https://catalog.example.test/catalog?token=secret",
        "https://catalog.example.test/catalog#private",
        "https://user:secret@catalog.example.test/catalog",
    ):
        payload["source_url"] = unsafe
        with pytest.raises(ValidationError):
            BrowserObservation.model_validate(payload)


def test_review_cannot_be_repeated() -> None:
    reviewed = review_observation(
        _observation(),
        decision=ObservationDecision.ACCEPTED,
        reviewed_at=CAPTURED + timedelta(seconds=1),
    )

    with pytest.raises(ValueError, match="already been reviewed"):
        review_observation(
            reviewed,
            decision=ObservationDecision.REJECTED,
            reviewed_at=CAPTURED + timedelta(seconds=2),
            reason="Changed my mind.",
        )
