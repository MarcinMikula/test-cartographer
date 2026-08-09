
"""Build one process-specific candidate ContextBundle from accepted reused knowledge."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.context.enums import EvidenceSourceType, KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import (
    ComponentContext,
    ContextBundle,
    Evidence,
    KnowledgeText,
    LocatorCandidate,
    PageContext,
    ProcessContext,
    TestDataRequirement,
    UIElement,
)
from test_cartographer.expansion.enums import ExpansionDisposition, ExpansionPlanStatus
from test_cartographer.expansion.fingerprints import context_sha256
from test_cartographer.expansion.models import ExpansionPlan, ExpansionRequest
from test_cartographer.proactive_regression.enums import ChangeDisposition
from test_cartographer.proactive_regression.models import (
    ApprovedObservationItem,
    ElementRegressionObservation,
)


def observed_element_from_regression(
    item: ApprovedObservationItem,
    observation: ElementRegressionObservation,
    *,
    evidence_id: str,
    observed_at: datetime,
    sensitivity: SensitivityLevel = SensitivityLevel.PUBLIC,
) -> tuple[UIElement, Evidence]:
    """Convert accepted currentness evidence into a normal observed ContextBundle element."""

    if observation.element_id != item.element_id or observation.item_id != item.id:
        raise ValueError("regression observation does not belong to inventory item")
    if observation.disposition in {ChangeDisposition.MISSING, ChangeDisposition.AMBIGUOUS}:
        raise ValueError("missing or ambiguous target cannot become observed expansion evidence")
    if observation.current_locator_strategy is not None:
        strategy = observation.current_locator_strategy
        locator_value = observation.current_locator_value
    else:
        strategy = observation.expected_locator_strategy
        locator_value = observation.expected_locator_value
    assert locator_value is not None
    evidence = Evidence(
        id=evidence_id,
        source_type=EvidenceSourceType.APPLICATION,
        source_ref=f"proactive_regression:{observation.observation_sha256}",
        summary=f"Bounded expansion observation for {item.accessible_name}.",
        captured_at=observed_at,
        sensitivity=sensitivity,
        content_sha256=observation.observation_sha256,
    )
    knowledge = lambda value: KnowledgeText(
        value=value,
        status=KnowledgeStatus.OBSERVED,
        evidence_ids=(evidence_id,),
        sensitivity=sensitivity,
    )
    element = UIElement(
        id=item.element_id,
        owner_id=item.page_id,
        name=knowledge(item.accessible_name),
        semantic_role=knowledge(item.semantic_role),
        locator_candidates=(
            LocatorCandidate(
                id=f"loc_{item.element_id.removeprefix('el_')}_expansion",
                strategy=strategy,
                value=knowledge(locator_value),
                primary=True,
            ),
        ),
    )
    return element, evidence


def build_candidate_expansion_context(
    request: ExpansionRequest,
    plan: ExpansionPlan,
    base_context: ContextBundle,
    target_process: ProcessContext,
    *,
    candidate_context_id: str,
    title: str,
    created_at: datetime,
    observed_elements: tuple[UIElement, ...] = (),
    additional_evidence: tuple[Evidence, ...] = (),
    test_data: tuple[TestDataRequirement, ...] = (),
) -> ContextBundle:
    """Derive a new one-process bundle without mutating the accepted base bundle."""

    if plan.status is not ExpansionPlanStatus.ACCEPTED:
        raise ValueError("candidate expansion context requires a human-accepted expansion plan")
    if request.id != plan.request_id:
        raise ValueError("expansion plan does not belong to supplied request")
    if request.base_context_id != base_context.id or plan.base_context_id != base_context.id:
        raise ValueError("expansion artefacts do not belong to supplied base context")
    actual_hash = context_sha256(base_context)
    if request.base_context_sha256 != actual_hash or plan.base_context_sha256 != actual_hash:
        raise ValueError("base context changed after expansion planning")
    if target_process.id != request.target_process_id:
        raise ValueError("target process does not match expansion request")

    item_by_source = {
        item.source_id: item
        for item in plan.items
        if item.source_id is not None and item.subject_ref.startswith("elements.")
    }
    observed_by_id = {item.id: item for item in observed_elements}
    if len(observed_by_id) != len(observed_elements):
        raise ValueError("observed expansion element ids must be unique")
    base_by_id = {item.id: item for item in base_context.elements}

    required_element_ids = {
        step.action.target_element_id
        for step in target_process.steps
        if step.action.target_element_id is not None
    } | {
        element_id
        for outcome in target_process.expected_outcomes
        for element_id in outcome.related_element_ids
    }
    elements: list[UIElement] = []
    for element_id in sorted(required_element_ids):
        plan_item = item_by_source.get(element_id)
        observed = observed_by_id.get(element_id)
        base = base_by_id.get(element_id)
        if plan_item is not None and plan_item.disposition in {
            ExpansionDisposition.REOBSERVE,
            ExpansionDisposition.OBSERVE_NEW,
        }:
            if observed is None:
                raise ValueError(f"expansion target requires fresh observation: {element_id}")
            elements.append(observed)
            continue
        if observed is not None:
            elements.append(observed)
            continue
        if base is None:
            raise ValueError(f"candidate context lacks required element: {element_id}")
        elements.append(base)

    owner_ids = {item.owner_id for item in elements}
    base_pages = {page.id: page for page in base_context.pages}
    base_components = {component.id: component for component in base_context.components}
    page_ids = {step.page_id for step in target_process.steps}
    components: list[ComponentContext] = []
    component_ids = {owner for owner in owner_ids if owner in base_components}
    for component_id in sorted(component_ids):
        component = base_components[component_id]
        kept = tuple(item.id for item in elements if item.owner_id == component_id)
        components.append(component.model_copy(update={"element_ids": kept}))
        for page in base_context.pages:
            if component_id in page.component_ids:
                page_ids.add(page.id)

    pages: list[PageContext] = []
    for page_id in sorted(page_ids):
        page = base_pages.get(page_id)
        if page is None:
            raise ValueError(f"target process references page absent from base context: {page_id}")
        direct = tuple(item.id for item in elements if item.owner_id == page_id)
        contained_components = tuple(
            component.id for component in components if component.id in page.component_ids
        )
        pages.append(
            page.model_copy(
                update={
                    "element_ids": direct,
                    "component_ids": contained_components,
                }
            )
        )

    evidence_by_id = {item.id: item for item in (*base_context.evidence, *additional_evidence)}
    if len(evidence_by_id) != len(base_context.evidence) + len(additional_evidence):
        raise ValueError("additional expansion evidence ids must not collide with base evidence")

    candidate = ContextBundle(
        id=candidate_context_id,
        title=title,
        created_at=created_at,
        updated_at=created_at,
        application=base_context.application,
        process=target_process,
        pages=tuple(pages),
        components=tuple(components),
        elements=tuple(elements),
        test_data=test_data,
        evidence=tuple(evidence_by_id[key] for key in sorted(evidence_by_id)),
        open_questions=(),
        conflicts=(),
    )
    return candidate
