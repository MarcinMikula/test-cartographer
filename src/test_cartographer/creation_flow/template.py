"""Deterministic reference POM proposal for the bounded Sprint 10 demo flow."""

from __future__ import annotations

import json

from test_cartographer.context.enums import ActionKind
from test_cartographer.synthesis.models import BoundedSynthesisRequest


def render_reference_pom_proposal(request: BoundedSynthesisRequest) -> str:
    """Render one exact proposal from the accepted single-page search contract."""

    if len(request.pages) != 1:
        raise ValueError("reference demo synthesis requires exactly one page")
    if len(request.components) != 1:
        raise ValueError("reference demo synthesis requires exactly one component")

    page = request.pages[0]
    component = request.components[0]
    steps = sorted(request.steps, key=lambda item: item.order)
    by_kind = {step.action.kind: step for step in steps}
    required = {ActionKind.NAVIGATE, ActionKind.FILL, ActionKind.CLICK, ActionKind.READ}
    if not required.issubset(by_kind):
        raise ValueError("reference demo synthesis requires navigate, fill, click, and read steps")

    element_by_id = {item.id: item for item in request.elements}

    def action(step, method_id: str, method_name: str, owner_kind: str, owner_source_id: str):
        element = element_by_id.get(step.action.target_element_id)
        return {
            "id": method_id,
            "name": method_name,
            "owner_kind": owner_kind,
            "owner_source_id": owner_source_id,
            "intent": step.intent.value,
            "actions": [
                {
                    "step_id": step.id,
                    "kind": step.action.kind.value,
                    "target_element_id": step.action.target_element_id,
                    "locator_id": None if element is None else element.primary_locator.id,
                    "test_data_id": step.action.test_data_id,
                }
            ],
        }

    navigate = by_kind[ActionKind.NAVIGATE]
    fill = by_kind[ActionKind.FILL]
    click = by_kind[ActionKind.CLICK]
    read = by_kind[ActionKind.READ]
    outcome = request.outcomes[0]
    proposal = {
        "schema_version": "0.1",
        "id": "proposal_creation_demo",
        "request_id": request.id,
        "context_id": request.context_id,
        "summary": "Represent the discovered catalog page and search form as reviewed POM objects with one method per accepted process step.",
        "pages": [
            {
                "id": "pom_page_catalog",
                "class_name": "CatalogPage",
                "source_page_id": page.id,
                "method_ids": ["method_open_catalog", "method_read_results"],
                "component_object_ids": ["pom_component_search_form"],
            }
        ],
        "components": [
            {
                "id": "pom_component_search_form",
                "class_name": "CatalogSearchForm",
                "source_component_id": component.id,
                "method_ids": ["method_enter_query", "method_submit_search"],
            }
        ],
        "methods": [
            action(navigate, "method_open_catalog", "open_catalog", "page", page.id),
            action(fill, "method_enter_query", "enter_query", "component", component.id),
            action(click, "method_submit_search", "submit_search", "component", component.id),
            action(read, "method_read_results", "read_results", "page", page.id),
        ],
        "fixtures": [
            {
                "id": "fixture_catalog_context",
                "name": "catalog_context",
                "purpose": "Provide the reviewed environment and explicit non-secret symbolic query.",
                "uses_role_from_context": True,
                "uses_environment_from_context": True,
                "secret_values_included": False,
            }
        ],
        "test": {
            "id": "test_creation_catalog_search",
            "name": "test_search_catalog",
            "process_id": request.process_id,
            "fixture_ids": ["fixture_catalog_context"],
            "method_ids": [
                "method_open_catalog",
                "method_enter_query",
                "method_submit_search",
                "method_read_results",
            ],
            "assertions": [
                {
                    "id": "assert_creation_matching_results",
                    "outcome_id": outcome.id,
                    "page_id": page.id,
                    "related_element_ids": list(outcome.related_element_ids),
                    "intent": "Verify the confirmed visible result without claiming broader business correctness.",
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
