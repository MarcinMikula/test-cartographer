from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
from pydantic import ValidationError

from test_cartographer.context.io import load_context
from test_cartographer.context.models import ContextBundle, KnowledgeText

ROOT = Path(__file__).resolve().parents[3]
VALID_FIXTURE = ROOT / "testdata" / "context" / "valid" / "public_search_flow.json"


def _valid_payload() -> dict:
    return load_context(VALID_FIXTURE).model_dump(mode="json")


def test_valid_reference_context_loads() -> None:
    context = load_context(VALID_FIXTURE)

    assert context.schema_version == "0.1"
    assert context.process.id == "proc_search_catalog"
    assert len(context.process.steps) == 4
    assert len(context.elements) == 4


def test_unknown_knowledge_is_explicit_and_value_free() -> None:
    value = KnowledgeText(
        value=None,
        status="unknown",
        evidence_ids=(),
        confidence=None,
        sensitivity="internal",
        notes=None,
    )

    assert value.value is None
    assert value.status.value == "unknown"


def test_unknown_knowledge_rejects_selected_value() -> None:
    with pytest.raises(ValidationError, match="unknown knowledge must not contain"):
        KnowledgeText(
            value="guessed value",
            status="unknown",
            evidence_ids=(),
            sensitivity="internal",
        )


def test_inferred_knowledge_requires_confidence() -> None:
    with pytest.raises(ValidationError, match="inferred knowledge requires confidence"):
        KnowledgeText(
            value="button:Search",
            status="inferred",
            evidence_ids=("ev_app_catalog",),
            sensitivity="public",
        )


def test_conflicting_knowledge_requires_two_evidence_items() -> None:
    with pytest.raises(ValidationError, match="at least two evidence"):
        KnowledgeText(
            value=None,
            status="conflicting",
            evidence_ids=("ev_app_catalog",),
            sensitivity="public",
        )


def test_extra_contract_fields_are_rejected() -> None:
    payload = _valid_payload()
    payload["unexpected"] = "not allowed"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        ContextBundle.model_validate(payload)


def test_duplicate_ids_are_rejected_globally() -> None:
    payload = _valid_payload()
    payload["pages"][0]["id"] = payload["process"]["id"]

    with pytest.raises(ValidationError, match="ids must be globally unique"):
        ContextBundle.model_validate(payload)


def test_non_contiguous_step_order_is_rejected() -> None:
    payload = _valid_payload()
    payload["process"]["steps"][2]["order"] = 4

    with pytest.raises(ValidationError, match="step order must be contiguous"):
        ContextBundle.model_validate(payload)


def test_fill_action_without_test_data_is_rejected() -> None:
    payload = _valid_payload()
    payload["process"]["steps"][1]["action"]["test_data_id"] = None

    with pytest.raises(ValidationError, match="fill action requires test_data_id"):
        ContextBundle.model_validate(payload)


def test_unknown_element_reference_is_rejected() -> None:
    payload = _valid_payload()
    payload["process"]["steps"][1]["action"]["target_element_id"] = "el_missing"

    with pytest.raises(ValidationError, match="references unknown element"):
        ContextBundle.model_validate(payload)


def test_element_owner_must_match_page_or_component_listing() -> None:
    payload = _valid_payload()
    payload["elements"][0]["owner_id"] = "page_catalog"

    with pytest.raises(ValidationError, match="owner does not match"):
        ContextBundle.model_validate(payload)


def test_dangling_evidence_reference_is_rejected() -> None:
    invalid = (
        ROOT
        / "testdata"
        / "context"
        / "invalid"
        / "missing_evidence_reference.json"
    )

    with pytest.raises(ValidationError, match="unknown evidence"):
        load_context(invalid)


def test_two_primary_locators_are_rejected() -> None:
    payload = _valid_payload()
    element = payload["elements"][0]
    second = deepcopy(element["locator_candidates"][0])
    second["id"] = "loc_search_input_test_id"
    second["strategy"] = "test_id"
    second["value"]["value"] = "search-input"
    element["locator_candidates"].append(second)

    with pytest.raises(ValidationError, match="at most one primary locator"):
        ContextBundle.model_validate(payload)


def test_action_target_must_be_available_on_step_page() -> None:
    payload = _valid_payload()
    payload["pages"][0]["component_ids"] = []

    with pytest.raises(ValidationError, match="is not available on page"):
        ContextBundle.model_validate(payload)


def test_test_data_symbolic_refs_must_be_unique() -> None:
    payload = _valid_payload()
    duplicate = deepcopy(payload["test_data"][0])
    duplicate["id"] = "data_second_query"
    payload["test_data"].append(duplicate)

    with pytest.raises(ValidationError, match="symbolic_ref values must be unique"):
        ContextBundle.model_validate(payload)
