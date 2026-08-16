"""Deterministic proposals for reviewed external single-page flows."""

from __future__ import annotations

import json
import re

from test_cartographer.context.enums import ActionKind
from test_cartographer.synthesis.models import BoundedSynthesisRequest

_WORD = re.compile(r"[A-Za-z0-9]+")


def render_external_single_page_proposal(request: BoundedSynthesisRequest) -> str:
    """Render one bounded proposal without inventing actions or test data."""

    if len(request.pages) != 1:
        raise ValueError("external single-page synthesis requires exactly one page")

    steps = sorted(request.steps, key=lambda item: item.order)
    if _is_legacy_heading_request(request, steps):
        return _render_heading_proposal(request, steps)
    return _render_rich_proposal(request, steps)


def _is_legacy_heading_request(request, steps) -> bool:
    if request.components or request.test_data or len(steps) != 2:
        return False
    navigate, read = steps
    if (
        navigate.action.kind is not ActionKind.NAVIGATE
        or read.action.kind is not ActionKind.READ
        or read.action.target_element_id is None
    ):
        return False
    element = next(
        (item for item in request.elements if item.id == read.action.target_element_id),
        None,
    )
    return element is not None and element.semantic_role.value.casefold() == "heading"


def _render_heading_proposal(request: BoundedSynthesisRequest, steps) -> str:
    """Preserve the exact reviewed navigate/read-heading proposal."""

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


def _render_rich_proposal(request: BoundedSynthesisRequest, steps) -> str:
    if not 3 <= len(steps) <= 7:
        raise ValueError(
            "external single-page rich synthesis requires between three and seven steps"
        )
    if steps[0].action.kind is not ActionKind.NAVIGATE:
        raise ValueError("external single-page rich synthesis must begin with navigate")
    if any(item.action.kind is ActionKind.NAVIGATE for item in steps[1:]):
        raise ValueError("external single-page rich synthesis allows one navigate step")
    if not any(item.action.kind is not ActionKind.READ for item in steps[1:]):
        raise ValueError("external single-page rich synthesis requires one interaction")
    reads = [item for item in steps[1:] if item.action.kind is ActionKind.READ]
    if reads != [steps[-1]]:
        raise ValueError(
            "external single-page rich synthesis requires one final read step"
        )
    if any(item.page_id != request.pages[0].id for item in steps):
        raise ValueError("external single-page rich synthesis requires one page for all steps")

    allowed_actions = {
        ActionKind.FILL,
        ActionKind.CLICK,
        ActionKind.SELECT,
        ActionKind.CHECK,
        ActionKind.UNCHECK,
        ActionKind.READ,
    }
    unexpected = sorted(
        {
            item.action.kind.value
            for item in steps[1:]
            if item.action.kind not in allowed_actions
        }
    )
    if unexpected:
        raise ValueError(
            f"unsupported external single-page rich actions: {unexpected}"
        )

    page = request.pages[0]
    component_by_id = {item.id: item for item in request.components}
    element_by_id = {item.id: item for item in request.elements}
    declared_owners = {page.id, *component_by_id}
    for step in steps[1:]:
        target_id = step.action.target_element_id
        element = element_by_id.get(target_id)
        if element is None or element.owner_id not in declared_owners:
            raise ValueError(
                f"external single-page rich step has an undeclared target: {step.id}"
            )

    if len(request.outcomes) != 1:
        raise ValueError("external single-page rich synthesis requires one outcome")
    outcome = request.outcomes[0]
    final_target_id = steps[-1].action.target_element_id
    if outcome.related_element_ids != (final_target_id,):
        raise ValueError(
            "external single-page rich outcome must reference the final read target"
        )

    methods = []
    page_method_ids: list[str] = []
    component_method_ids: dict[str, list[str]] = {
        component.id: [] for component in request.components
    }
    ordered_method_ids: list[str] = []

    for index, step in enumerate(steps, start=1):
        method_id = f"method_external_{index:02d}"
        if step.action.kind is ActionKind.NAVIGATE:
            owner_kind = "page"
            owner_source_id = page.id
            method_name = "open_page"
            target = None
        else:
            target = element_by_id[step.action.target_element_id]
            owner_source_id = target.owner_id
            owner_kind = "page" if owner_source_id == page.id else "component"
            method_name = _step_method_name(step.action.kind, target.name.value, index)

        method = {
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
                    "locator_id": None if target is None else target.primary_locator.id,
                    "test_data_id": step.action.test_data_id,
                }
            ],
        }
        methods.append(method)
        ordered_method_ids.append(method_id)
        if owner_kind == "page":
            page_method_ids.append(method_id)
        else:
            component_method_ids[owner_source_id].append(method_id)

    proposed_components = []
    component_object_ids = []
    for index, component in enumerate(request.components, start=1):
        proposal_id = f"pom_external_component_{index:02d}"
        component_object_ids.append(proposal_id)
        proposed_components.append(
            {
                "id": proposal_id,
                "class_name": _component_class_name(component.name.value),
                "source_component_id": component.id,
                "method_ids": component_method_ids[component.id],
            }
        )

    proposal = {
        "schema_version": "0.1",
        "id": "proposal_external_single_page_rich",
        "request_id": request.id,
        "context_id": request.context_id,
        "summary": (
            "Represent one reviewed multi-action external page as bounded Page "
            "Object and Component objects with a final visible outcome read."
        ),
        "pages": [
            {
                "id": "pom_external_page",
                "class_name": _class_name(page.name.value),
                "source_page_id": page.id,
                "method_ids": page_method_ids,
                "component_object_ids": component_object_ids,
            }
        ],
        "components": proposed_components,
        "methods": methods,
        "fixtures": [
            {
                "id": "fixture_external_page_context",
                "name": "external_page_context",
                "purpose": (
                    "Provide the reviewed environment URL, isolated browser session, "
                    "and explicit non-secret test data."
                ),
                "uses_role_from_context": True,
                "uses_environment_from_context": True,
                "secret_values_included": False,
            }
        ],
        "test": {
            "id": "test_external_single_page_rich",
            "name": f"test_{_snake_case(request.process_name.value)}",
            "process_id": request.process_id,
            "fixture_ids": ["fixture_external_page_context"],
            "method_ids": ordered_method_ids,
            "assertions": [
                {
                    "id": "assert_external_visible_outcome",
                    "outcome_id": outcome.id,
                    "page_id": page.id,
                    "related_element_ids": list(outcome.related_element_ids),
                    "intent": (
                        "Verify the reviewed visible post-interaction outcome without "
                        "claiming broader third-party application correctness."
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


def _component_class_name(value: str) -> str:
    words = _WORD.findall(value)
    body = "".join(word[:1].upper() + word[1:] for word in words) or "External"
    if body[0].isdigit():
        body = f"Component{body}"
    if not body.endswith("Component"):
        body += "Component"
    return body[:80]


def _step_method_name(kind: ActionKind, element_name: str, index: int) -> str:
    target = _snake_case(element_name)[:60]
    return f"{kind.value}_{target}_{index:02d}"[:80]
