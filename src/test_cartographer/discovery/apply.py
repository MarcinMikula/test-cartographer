"""Apply one accepted discovery to the ContextBundle graph."""

from __future__ import annotations

import hashlib
from pathlib import PurePosixPath

from test_cartographer.context.enums import (
    ActionKind,
    EvidenceSourceType,
    KnowledgeStatus,
    SensitivityLevel,
)
from test_cartographer.context.models import (
    ApplicationContext,
    ComponentContext,
    ContextBundle,
    Evidence,
    ExpectedOutcome,
    KnowledgeText,
    LocatorCandidate,
    PageContext,
    ProcessContext,
    ProcessStep,
    TestDataRequirement,
    UIAction,
    UIElement,
)
from test_cartographer.discovery.enums import DiscoveryDecision
from test_cartographer.discovery.models import (
    DiscoveryTarget,
    ElementCandidate,
    ProcessDiscoveryPlan,
    ProcessDiscoveryRun,
)


def apply_accepted_discovery(
    context: ContextBundle,
    plan: ProcessDiscoveryPlan,
    run: ProcessDiscoveryRun,
) -> ContextBundle:
    if run.decision is not DiscoveryDecision.ACCEPTED:
        raise ValueError("only accepted discovery can update context")
    if run.reviewed_at is None:
        raise ValueError("accepted discovery requires reviewed_at")
    if context.id != plan.context_id or context.id != run.context_id:
        raise ValueError("context identity does not match discovery")
    if plan.id != run.plan_id:
        raise ValueError("plan identity does not match discovery run")

    candidates = {item.id: item for item in run.candidates}
    results = {item.target_id: item for item in run.targets}
    evidence = tuple(_evidence(target, run, plan.sensitivity) for target in plan.targets)
    evidence_by_target = {target.id: evidence[index].id for index, target in enumerate(plan.targets)}

    selected_candidates = {
        target.id: candidates[results[target.id].selected_candidate_id]
        for target in plan.targets
    }
    elements = tuple(
        _element(target, selected_candidates[target.id], evidence_by_target[target.id])
        for target in plan.targets
    )
    observed_page_name = next(
        (
            selected_candidates[target.id].semantic_name
            for target in plan.targets
            if target.outcome_target
        ),
        plan.page_name,
    )
    components = tuple(
        ComponentContext(
            id=component_id,
            name=_observed(_humanize(component_id), tuple(evidence_by_target.values())),
            element_ids=tuple(target.element_id for target in plan.targets if target.owner_id == component_id),
        )
        for component_id in plan.component_ids
    )
    page = PageContext(
        id=plan.page_id,
        name=_observed(observed_page_name, tuple(evidence_by_target.values())),
        route=_observed(plan.route, tuple(evidence_by_target.values()), sensitivity=context.pages[0].route.sensitivity),
        component_ids=plan.component_ids,
        element_ids=tuple(target.element_id for target in plan.targets if target.owner_id == plan.page_id),
    )
    test_data = tuple(
        TestDataRequirement(
            id=f"td_{target.test_data_symbolic_ref}",
            name=_observed(_humanize(target.test_data_symbolic_ref), (evidence_by_target[target.id],)),
            description=_observed(
                f"Symbolic value used by the {target.name} step.",
                (evidence_by_target[target.id],),
            ),
            symbolic_ref=target.test_data_symbolic_ref,
            sensitivity=context.application.base_url.sensitivity,
        )
        for target in plan.targets
        if target.test_data_symbolic_ref is not None
    )
    existing_intent = context.process.steps[0].intent
    steps = [
        ProcessStep(
            id="step_open_page",
            order=1,
            page_id=page.id,
            intent=existing_intent,
            action=UIAction(kind=ActionKind.NAVIGATE),
            expected_state=_observed("The target page is available.", tuple(evidence_by_target.values())),
        )
    ]
    for index, target in enumerate(plan.targets, start=2):
        steps.append(
            ProcessStep(
                id=f"step_{target.id}",
                order=index,
                page_id=page.id,
                intent=_observed(_intent(target), (evidence_by_target[target.id],)),
                action=UIAction(
                    kind=target.action_kind,
                    target_element_id=target.element_id,
                    test_data_id=(
                        f"td_{target.test_data_symbolic_ref}"
                        if target.test_data_symbolic_ref is not None
                        else None
                    ),
                ),
                expected_state=_observed(_expected_state(target), (evidence_by_target[target.id],)),
            )
        )
    outcome_target_ids = tuple(target.element_id for target in plan.targets if target.outcome_target)
    existing_outcome = context.process.expected_outcomes[0]
    process = ProcessContext(
        id=context.process.id,
        name=context.process.name,
        purpose=context.process.purpose,
        risk=context.process.risk,
        role=context.process.role,
        preconditions=context.process.preconditions,
        steps=tuple(steps),
        expected_outcomes=(
            ExpectedOutcome(
                id=existing_outcome.id,
                statement=existing_outcome.statement,
                related_element_ids=outcome_target_ids,
            ),
        ),
    )
    application = ApplicationContext(
        id=context.application.id,
        name=context.application.name,
        environment=context.application.environment,
        base_url=_observed(run.source_url, tuple(evidence_by_target.values()), sensitivity=context.application.base_url.sensitivity),
    )
    updated = context.model_copy(
        update={
            "updated_at": run.reviewed_at,
            "application": application,
            "process": process,
            "pages": (page,),
            "components": components,
            "elements": elements,
            "test_data": test_data,
            "evidence": (*context.evidence, *evidence),
            "open_questions": (),
            "conflicts": (),
        }
    )
    return ContextBundle.model_validate(updated.model_dump(mode="python"))


def _element(target: DiscoveryTarget, candidate: ElementCandidate, evidence_id: str) -> UIElement:
    unique = sorted(
        (item for item in candidate.locator_candidates if item.match_count == 1),
        key=lambda item: (item.priority, item.id),
    )
    if not unique:
        raise ValueError(f"selected candidate {candidate.id} has no unique locator")
    locators = tuple(
        LocatorCandidate(
            id=f"loc_{target.element_id}_{index}",
            strategy=item.strategy,
            value=_observed(item.value, (evidence_id,)),
            primary=index == 1,
        )
        for index, item in enumerate(unique, start=1)
    )
    return UIElement(
        id=target.element_id,
        owner_id=target.owner_id,
        name=_observed(candidate.semantic_name, (evidence_id,)),
        semantic_role=_observed(candidate.semantic_role, (evidence_id,)),
        locator_candidates=locators,
    )


def _evidence(
    target: DiscoveryTarget,
    run: ProcessDiscoveryRun,
    sensitivity: SensitivityLevel,
) -> Evidence:
    digest = hashlib.sha256(f"{run.id}:{target.id}".encode("utf-8")).hexdigest()[:16]
    return Evidence(
        id=f"ev_discovery_{digest}",
        source_type=EvidenceSourceType.APPLICATION,
        source_ref=f"process_discovery:{run.id}:{target.id}",
        summary=f"Accepted bounded browser discovery for {target.name}.",
        captured_at=run.captured_at,
        sensitivity=sensitivity,
        content_sha256=run.capture_sha256,
    )


def _observed(value: str, evidence_ids: tuple[str, ...], *, sensitivity=None) -> KnowledgeText:
    return KnowledgeText(
        value=value,
        status=KnowledgeStatus.OBSERVED,
        evidence_ids=tuple(dict.fromkeys(evidence_ids)),
        sensitivity=sensitivity or SensitivityLevel.INTERNAL,
    )


def _intent(target: DiscoveryTarget) -> str:
    verbs = {
        "fill": f"Enter the symbolic value for {target.name}.",
        "click": f"Use {target.name}.",
        "select": f"Select the symbolic value for {target.name}.",
        "check": f"Select {target.name}.",
        "uncheck": f"Clear {target.name}.",
        "read": f"Observe {target.name}.",
    }
    return verbs.get(target.action_kind.value, f"Use {target.name}.")


def _expected_state(target: DiscoveryTarget) -> str:
    values = {
        "fill": f"The {target.name} value is supplied during execution.",
        "click": f"The {target.name} action completes.",
        "select": f"The {target.name} option is selected during execution.",
        "check": f"The {target.name} option is selected.",
        "uncheck": f"The {target.name} option is cleared.",
        "read": f"The {target.name} is visible and can be asserted.",
    }
    return values.get(target.action_kind.value, f"The {target.name} step completes.")


def _humanize(identifier: str) -> str:
    return PurePosixPath(identifier).name.replace("_", " ").strip().title()
