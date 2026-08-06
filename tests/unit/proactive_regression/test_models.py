from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.proactive_regression.enums import (
    AuthenticationMode,
    InventoryReviewDecision,
)


def test_reference_inventory_is_human_accepted_and_bounded(inventory) -> None:
    assert inventory.human_approved is True
    assert inventory.review_decision is InventoryReviewDecision.ACCEPTED
    assert len(inventory.items) == inventory.budget.max_elements == 2


def test_inventory_rejects_non_public_sensitivity(inventory) -> None:
    with pytest.raises(ValidationError, match="must be PUBLIC"):
        inventory.model_copy(update={"sensitivity": SensitivityLevel.INTERNAL}).model_validate(
            {**inventory.model_dump(), "sensitivity": "internal"}
        )


def test_inventory_rejects_authentication(inventory) -> None:
    data = inventory.model_dump(mode="json")
    data["authentication_mode"] = "storage_state"
    with pytest.raises(ValidationError):
        type(inventory).model_validate(data)


def test_inventory_rejects_unallowlisted_item_route(inventory) -> None:
    data = inventory.model_dump(mode="json")
    data["items"][0]["route"] = "/unknown"
    with pytest.raises(ValidationError, match="not allowlisted"):
        type(inventory).model_validate(data)


def test_profile_rejects_parent_traversal(profile) -> None:
    data = profile.model_dump(mode="json")
    data["current_document"] = "../secret.html"
    with pytest.raises(ValidationError, match="must not traverse"):
        type(profile).model_validate(data)


def test_inventory_acceptance_timestamp_must_be_aware(inventory) -> None:
    data = inventory.model_dump(mode="json")
    data["accepted_at"] = datetime(2026, 8, 6).isoformat()
    with pytest.raises(ValidationError, match="timezone"):
        type(inventory).model_validate(data)
