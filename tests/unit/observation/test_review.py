from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from test_cartographer.context.enums import KnowledgeStatus, LocatorStrategy, SensitivityLevel
from test_cartographer.context.io import load_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.observation.enums import ObservationDecision, ObservedAttributeName
from test_cartographer.observation.models import (
    BrowserObservation,
    ElementSnapshot,
    LocatorVerification,
    ObservedAttribute,
)
from test_cartographer.observation.review import (
    apply_accepted_observation,
    review_observation,
)

ROOT = Path(__file__).resolve().parents[3]
CAPTURED = datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc)


def _context():
    return load_context(
        ROOT / "testdata/context/observation_ready/public_search_flow.json"
    )


def _accepted() -> BrowserObservation:
    pending = BrowserObservation(
        id="obs_search_submit",
        context_id="ctx_public_catalog_search_observation_ready",
        target_element_id="el_search_submit",
        target_locator_id="loc_search_submit_role",
        source_url="https://catalog.example.test/catalog",
        captured_at=CAPTURED,
        sensitivity=SensitivityLevel.PUBLIC,
        capture_seconds=0.3,
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
                    name=ObservedAttributeName.TEST_ID,
                    value="search-submit",
                ),
            ),
        ),
        capture_sha256="b" * 64,
    )
    return review_observation(
        pending,
        decision=ObservationDecision.ACCEPTED,
        reviewed_at=CAPTURED + timedelta(seconds=2),
        reason="The locator and target are correct.",
    )


def test_accepted_observation_removes_only_remaining_readiness_blocker() -> None:
    context = _context()
    before = assess_readiness(context)

    updated = apply_accepted_observation(context, _accepted())
    after = assess_readiness(updated)
    target = next(item for item in updated.elements if item.id == "el_search_submit")
    locator = next(item for item in target.locator_candidates if item.primary)

    assert before.blocker_count == 1
    assert before.issues[0].code == "primary_locator_not_observed"
    assert after.ready is True
    assert locator.value.status is KnowledgeStatus.OBSERVED
    assert len(updated.evidence) == len(context.evidence) + 1
    assert updated.process == context.process
    assert updated.pages == context.pages


def test_pending_or_rejected_observation_cannot_update_context() -> None:
    accepted = _accepted()
    pending = accepted.model_copy(
        update={
            "decision": ObservationDecision.PENDING,
            "reviewed_at": None,
            "review_reason": None,
        }
    )
    pending = BrowserObservation.model_validate(pending.model_dump(mode="python"))
    rejected = accepted.model_copy(
        update={
            "decision": ObservationDecision.REJECTED,
            "review_reason": "Wrong target.",
        }
    )
    rejected = BrowserObservation.model_validate(rejected.model_dump(mode="python"))

    for observation in (pending, rejected):
        with pytest.raises(ValueError, match="only an accepted"):
            apply_accepted_observation(_context(), observation)


def test_observation_must_match_context_locator_value() -> None:
    accepted = _accepted()
    mismatch = accepted.model_copy(
        update={
            "locator": accepted.locator.model_copy(update={"value": "button:Wrong"})
        }
    )
    mismatch = BrowserObservation.model_validate(mismatch.model_dump(mode="python"))

    with pytest.raises(ValueError, match="value does not match"):
        apply_accepted_observation(_context(), mismatch)
