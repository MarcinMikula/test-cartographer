"""Deterministic proposal for one reviewed external single-page heading flow."""

from __future__ import annotations

import json
import re

from test_cartographer.context.enums import ActionKind
from test_cartographer.synthesis.models import BoundedSynthesisRequest

_WORD = re.compile(r"[A-Za-z0-9]+")


def render_external_single_page_proposal(request: BoundedSynthesisRequest) -> str:
    """Render one strict navigate/read proposal without invented test data."""

    if len(request.pages) != 1:
        raise ValueError("external single-page synthesis requires exactly one page")
    if request.components:
        raise ValueError("external single-page heading synthesis does not require components")
    if request.test_data:
        raise ValueError("external single-page heading synthesis does not require test data")

    steps = sorted(request.steps, key=lambda item: item.order)
    navigate = [item for item in steps if item.action.kind is ActionKind.NAVIGATE]
    reads = [item for item in steps if item.action.kind is ActionKind.READ]
    if len(navigate) != 1 or len(reads) != 1 or len(steps) != 2:
        raise ValueError(
            "external single-page heading synthesis requires one navigate and one read step"
        )

    page = request.pages[0]
    read = reads[0]
    if read.action.target_element_id is None:
        raise ValueError("external single-page read step requires one target element")

    element_by_id = {item.id: item for item in request.elements}
    element = element_by_id.get(read.action.target_element_id)
    if element is None or element.owner_id != page.id:
        raise ValueError("external single-page read target must belong to the page")
    if element.semantic_role.value.casefold() != "heading":
        raise ValueError("external single-page read target must be an observed heading")

    outcome = request.outcomes[0]
    page_class = _class_name(page.name.value)
    test_name = f"test_{_snake_case(page.name.value)}"

    def action(step, method_id: str, method_name: str):
        target = element_by_id.get(step.action.target_element_id)
        return {
            "id": method_id,
            "name": method_name,
            "owner_kind": "page",
            "owner_source_id": page.id,
            "intent": step.intent.value,
            "actions": [
                {
                    "step_id": step.id,
                    "kind": step.action.kind.value,
                    "target_element_id": step.action.target_element_id,
                    "locator_id": None if target is None else target.primary_locator.id,
                    "test_data_id": step.action.test_data_id,
                }
            ],
        }

    proposal = {
        "schema_version": "0.1",
        "id": "proposal_external_single_page",
        "request_id": request.id,
        "context_id": request.context_id,
        "summary": (
            "Represent one observed external page and its reviewed heading outcome "
            "as a bounded Page Object and executable test."
        ),
        "pages": [
            {
                "id": "pom_external_page",
                "class_name": page_class,
                "source_page_id": page.id,
                "method_ids": ["method_open_page", "method_read_expected_heading"],
                "component_object_ids": [],
            }
        ],
        "components": [],
        "methods": [
            action(navigate[0], "method_open_page", "open_page"),
            action(read, "method_read_expected_heading", "read_expected_heading"),
        ],
        "fixtures": [
            {
                "id": "fixture_external_page_context",
                "name": "external_page_context",
                "purpose": (
                    "Provide the reviewed environment URL and one isolated browser "
                    "session without inventing test data."
                ),
                "uses_role_from_context": True,
                "uses_environment_from_context": True,
                "secret_values_included": False,
            }
        ],
        "test": {
            "id": "test_external_single_page",
            "name": test_name,
            "process_id": request.process_id,
            "fixture_ids": ["fixture_external_page_context"],
            "method_ids": ["method_open_page", "method_read_expected_heading"],
            "assertions": [
                {
                    "id": "assert_external_heading",
                    "outcome_id": outcome.id,
                    "page_id": page.id,
                    "related_element_ids": list(outcome.related_element_ids),
                    "intent": (
                        "Verify the reviewed observed heading without claiming "
                        "broader third-party application correctness."
                    ),
                }
            ],
        },
        "open_questions": [],
        "claim_flags": {
            "execution_success": False,
            "business_correctness": False,
            "locator_stability": False,
            "repository_fit": False,
            "security_approval": False,
        },
    }
    return json.dumps(proposal, ensure_ascii=False, sort_keys=True)


def _class_name(value: str) -> str:
    words = _WORD.findall(value)
    body = "".join(word[:1].upper() + word[1:] for word in words) or "External"
    if body[0].isdigit():
        body = f"Page{body}"
    if not body.endswith("Page"):
        body += "Page"
    return body[:80]


def _snake_case(value: str) -> str:
    words = _WORD.findall(value.casefold())
    return ("_".join(words) or "external_page")[:74]
