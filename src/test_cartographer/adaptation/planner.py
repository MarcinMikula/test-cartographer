"""Deterministic mapping from an accepted POM proposal to framework targets."""

from __future__ import annotations

import re
from datetime import datetime

from test_cartographer.adaptation.enums import (
    AdaptationOperationKind,
    AdaptationTargetKind,
)
from test_cartographer.adaptation.models import (
    AdaptationOperation,
    AdaptationPlan,
    FrameworkSnapshot,
    WorkspaceProfile,
)
from test_cartographer.synthesis.enums import SynthesisRunStatus
from test_cartographer.synthesis.models import SynthesisRun


def build_adaptation_plan(
    run: SynthesisRun,
    profile: WorkspaceProfile,
    snapshot: FrameworkSnapshot,
    *,
    plan_id: str,
    created_at: datetime,
) -> AdaptationPlan:
    if run.status is not SynthesisRunStatus.ACCEPTED or run.proposal is None:
        raise ValueError("adaptation planning requires an accepted synthesis run")
    if snapshot.profile_id != profile.id:
        raise ValueError("snapshot does not belong to the supplied workspace profile")

    proposal = run.proposal
    operations: list[AdaptationOperation] = []
    object_operation_ids: list[str] = []

    for index, page in enumerate(proposal.pages, start=1):
        required_methods, required_properties = _page_required_members(run, page.id)
        operation = _object_operation(
            snapshot,
            operation_id=f"adapt_page_{index:02d}",
            target_kind=AdaptationTargetKind.PAGE,
            target_path=f"pages/{_snake_case(page.class_name)}.py",
            symbol_name=page.class_name,
            source_ids=(page.id, page.source_page_id, *page.method_ids),
            rationale="Map the accepted logical Page Object to the framework pages layer.",
            required_method_names=required_methods,
            required_property_names=required_properties,
        )
        operations.append(operation)
        object_operation_ids.append(operation.id)

    for index, component in enumerate(proposal.components, start=1):
        required_methods, required_properties = _component_required_members(run, component.id)
        operation = _object_operation(
            snapshot,
            operation_id=f"adapt_component_{index:02d}",
            target_kind=AdaptationTargetKind.COMPONENT,
            target_path=f"components/{_snake_case(component.class_name)}.py",
            symbol_name=component.class_name,
            source_ids=(component.id, component.source_component_id, *component.method_ids),
            rationale="Map the accepted logical component to the framework components layer.",
            required_method_names=required_methods,
            required_property_names=required_properties,
        )
        operations.append(operation)
        object_operation_ids.append(operation.id)

    fixture_operation_ids: list[str] = []
    for index, fixture in enumerate(proposal.fixtures, start=1):
        operation = _symbol_operation(
            snapshot,
            operation_id=f"adapt_fixture_{index:02d}",
            target_kind=AdaptationTargetKind.FIXTURE,
            target_path="tests/e2e/conftest.py",
            symbol_name=fixture.name,
            source_ids=(fixture.id,),
            rationale="Add or reuse the symbolic pytest fixture required by the accepted proposal.",
        )
        operations.append(operation)
        fixture_operation_ids.append(operation.id)

    test_path = f"tests/e2e/{proposal.test.name}.py"
    test_operation = _symbol_operation(
        snapshot,
        operation_id="adapt_test_01",
        target_kind=AdaptationTargetKind.TEST,
        target_path=test_path,
        symbol_name=proposal.test.name,
        source_ids=(proposal.test.id, *proposal.test.method_ids, *(item.id for item in proposal.test.assertions)),
        rationale="Map the accepted test intent to the framework E2E layer without generating source code.",
        depends_on=tuple(object_operation_ids + fixture_operation_ids),
    )
    operations.append(test_operation)

    open_questions = tuple(item.question for item in proposal.open_questions)
    return AdaptationPlan(
        id=plan_id,
        workspace_profile_id=profile.id,
        snapshot_id=snapshot.id,
        snapshot_fingerprint=snapshot.root_fingerprint,
        synthesis_run_id=run.id,
        proposal_id=proposal.id,
        context_id=proposal.context_id,
        created_at=created_at,
        operations=tuple(operations),
        verification_commands=(
            "python -m compileall -q pages components tests testdata",
            "python -m pytest --collect-only -q",
            "python -m pytest tests/unit/ -v",
            "python -m pytest tests/e2e/ -v",
        ),
        open_questions=open_questions,
    )


def _object_operation(
    snapshot: FrameworkSnapshot,
    *,
    required_method_names: tuple[str, ...],
    required_property_names: tuple[str, ...],
    **kwargs,
) -> AdaptationOperation:
    entry = next((item for item in snapshot.entries if item.path == kwargs["target_path"]), None)
    if entry is None:
        return _operation(snapshot, **kwargs)
    symbol = next(
        (item for item in entry.python_symbols if item.name == kwargs["symbol_name"]),
        None,
    )
    if symbol is None:
        return _operation(snapshot, **kwargs)

    incompatible_methods = sorted(set(required_method_names) & set(symbol.property_names))
    incompatible_properties = sorted(set(required_property_names) & set(symbol.method_names))
    if incompatible_methods or incompatible_properties:
        raise ValueError(
            "existing class member kind conflicts with accepted proposal: "
            f"methods_as_properties={incompatible_methods}, "
            f"properties_as_methods={incompatible_properties}"
        )

    missing_methods = tuple(name for name in required_method_names if name not in symbol.method_names)
    missing_properties = tuple(
        name for name in required_property_names if name not in symbol.property_names
    )
    if not missing_methods and not missing_properties:
        return AdaptationOperation(
            id=kwargs["operation_id"],
            kind=AdaptationOperationKind.REUSE_SYMBOL,
            target_kind=kwargs["target_kind"],
            target_path=kwargs["target_path"],
            symbol_name=kwargs["symbol_name"],
            source_proposal_ids=kwargs["source_ids"],
            rationale=kwargs["rationale"],
            depends_on=kwargs.get("depends_on", ()),
        )
    return AdaptationOperation(
        id=kwargs["operation_id"],
        kind=AdaptationOperationKind.EXTEND_SYMBOL,
        target_kind=kwargs["target_kind"],
        target_path=kwargs["target_path"],
        symbol_name=kwargs["symbol_name"],
        source_proposal_ids=kwargs["source_ids"],
        rationale=kwargs["rationale"],
        method_names=missing_methods,
        property_names=missing_properties,
        depends_on=kwargs.get("depends_on", ()),
    )
def _symbol_operation(snapshot: FrameworkSnapshot, **kwargs) -> AdaptationOperation:
    return _operation(snapshot, **kwargs)


def _operation(
    snapshot: FrameworkSnapshot,
    *,
    operation_id: str,
    target_kind: AdaptationTargetKind,
    target_path: str,
    symbol_name: str,
    source_ids: tuple[str, ...],
    rationale: str,
    depends_on: tuple[str, ...] = (),
) -> AdaptationOperation:
    entry = next((item for item in snapshot.entries if item.path == target_path), None)
    if entry is None:
        kind = AdaptationOperationKind.CREATE_FILE
    elif any(symbol.name == symbol_name for symbol in entry.python_symbols):
        kind = AdaptationOperationKind.REUSE_SYMBOL
    else:
        kind = AdaptationOperationKind.ADD_SYMBOL
    return AdaptationOperation(
        id=operation_id,
        kind=kind,
        target_kind=target_kind,
        target_path=target_path,
        symbol_name=symbol_name,
        source_proposal_ids=source_ids,
        rationale=rationale,
        depends_on=depends_on,
    )



def _page_required_members(
    run: SynthesisRun,
    page_id: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    proposal = run.proposal
    assert proposal is not None
    page = next(item for item in proposal.pages if item.id == page_id)
    methods = [next(item for item in proposal.methods if item.id == method_id) for method_id in page.method_ids]
    method_names = tuple(dict.fromkeys(method.name for method in methods))
    required_element_ids = {
        action.target_element_id
        for method in methods
        for action in method.actions
        if action.target_element_id is not None
    }
    required_element_ids.update(
        element_id
        for assertion in proposal.test.assertions
        if assertion.page_id == page.source_page_id
        for element_id in assertion.related_element_ids
    )
    request_elements = {item.id: item for item in run.request.elements}
    property_names = tuple(
        _element_attribute(element_id)
        for element_id in sorted(required_element_ids)
        if element_id in request_elements
        and request_elements[element_id].owner_id == page.source_page_id
    )
    _reject_member_name_overlap(method_names, property_names, page.class_name)
    return method_names, tuple(dict.fromkeys(property_names))


def _component_required_members(
    run: SynthesisRun,
    component_id: str,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    proposal = run.proposal
    assert proposal is not None
    component = next(item for item in proposal.components if item.id == component_id)
    methods = [next(item for item in proposal.methods if item.id == method_id) for method_id in component.method_ids]
    method_names = tuple(dict.fromkeys(method.name for method in methods))
    required_element_ids = {
        action.target_element_id
        for method in methods
        for action in method.actions
        if action.target_element_id is not None
    }
    request_elements = {item.id: item for item in run.request.elements}
    property_names = tuple(
        _element_attribute(element_id)
        for element_id in sorted(required_element_ids)
        if element_id in request_elements
        and request_elements[element_id].owner_id == component.source_component_id
    )
    _reject_member_name_overlap(method_names, property_names, component.class_name)
    return method_names, tuple(dict.fromkeys(property_names))


def _reject_member_name_overlap(
    method_names: tuple[str, ...],
    property_names: tuple[str, ...],
    class_name: str,
) -> None:
    overlap = sorted(set(method_names) & set(property_names))
    if overlap:
        raise ValueError(
            f"accepted proposal creates method/property name collision in {class_name}: {overlap}"
        )
def _element_attribute(element_id: str) -> str:
    return _snake_case(re.sub(r"^el_", "", element_id))

def _snake_case(value: str) -> str:
    first = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first).lower()
