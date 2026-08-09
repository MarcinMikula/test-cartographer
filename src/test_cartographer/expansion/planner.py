
"""Deterministic reuse/gap planning for one incremental expansion request."""

from __future__ import annotations

from datetime import datetime

from test_cartographer.adaptation.models import FrameworkSnapshot
from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.context.models import ContextBundle, KnowledgeText
from test_cartographer.expansion.enums import (
    ExpansionDisposition,
    ExpansionPlanStatus,
    ExpansionReasonCode,
    ExpansionSubjectKind,
)
from test_cartographer.expansion.fingerprints import context_sha256
from test_cartographer.expansion.models import (
    ExpansionPlan,
    ExpansionPlanItem,
    ExpansionRequest,
)
from test_cartographer.proactive_regression.enums import ChangeDisposition
from test_cartographer.proactive_regression.models import (
    FrontendChangeReport,
    ObservationInventory,
)


def build_expansion_plan(
    request: ExpansionRequest,
    base_context: ContextBundle,
    snapshot: FrameworkSnapshot,
    *,
    plan_id: str,
    created_at: datetime,
    inventory: ObservationInventory | None = None,
    change_report: FrontendChangeReport | None = None,
) -> ExpansionPlan:
    """Classify what can be reused and what delta must be collected."""

    _validate_bindings(request, base_context, snapshot, inventory, change_report)
    items: list[ExpansionPlanItem] = []

    items.extend(
        (
            _knowledge_item(
                "exp_app_name",
                ExpansionSubjectKind.APPLICATION_VALUE,
                "application.name",
                base_context.application.id,
                base_context.application.name,
            ),
            _knowledge_item(
                "exp_app_environment",
                ExpansionSubjectKind.APPLICATION_VALUE,
                "application.environment",
                base_context.application.id,
                base_context.application.environment,
            ),
            _knowledge_item(
                "exp_app_base_url",
                ExpansionSubjectKind.APPLICATION_VALUE,
                "application.base_url",
                base_context.application.id,
                base_context.application.base_url,
            ),
        )
    )

    page_ids = _target_page_ids(request, base_context, inventory)
    page_by_id = {page.id: page for page in base_context.pages}
    for index, page_id in enumerate(sorted(page_ids), start=1):
        page = page_by_id.get(page_id)
        if page is None:
            items.append(
                ExpansionPlanItem(
                    id=f"exp_page_{index:02d}",
                    subject_kind=ExpansionSubjectKind.PAGE_VALUE,
                    subject_ref=f"pages.{page_id}",
                    source_id=page_id,
                    disposition=ExpansionDisposition.BLOCKED,
                    reason_code=ExpansionReasonCode.KNOWLEDGE_CONFLICT,
                )
            )
            continue
        items.append(
            _knowledge_item(
                f"exp_page_{index:02d}_name",
                ExpansionSubjectKind.PAGE_VALUE,
                f"pages.{page_id}.name",
                page_id,
                page.name,
            )
        )
        items.append(
            _knowledge_item(
                f"exp_page_{index:02d}_route",
                ExpansionSubjectKind.PAGE_VALUE,
                f"pages.{page_id}.route",
                page_id,
                page.route,
            )
        )

    base_elements = {element.id: element for element in base_context.elements}
    inventory_items = {} if inventory is None else {item.element_id: item for item in inventory.items}
    report_observations = (
        {} if change_report is None else {item.element_id: item for item in change_report.observations}
    )
    for index, element_id in enumerate(request.target_element_ids, start=1):
        base_element = base_elements.get(element_id)
        mapped = inventory_items.get(element_id)
        observation = report_observations.get(element_id)
        items.append(
            _target_element_item(
                item_id=f"exp_target_{index:02d}",
                element_id=element_id,
                base_element=base_element,
                mapped=mapped,
                observation=observation,
            )
        )

    # Process identity is supplied by the human request. The remaining business/test
    # meaning belongs to the new process and must not be inherited silently.
    items.append(
        ExpansionPlanItem(
            id="exp_process_name",
            subject_kind=ExpansionSubjectKind.PROCESS_VALUE,
            subject_ref="target_process.name",
            source_id=request.target_process_id,
            knowledge_status=KnowledgeStatus.PROVIDED,
            disposition=ExpansionDisposition.REVIEW,
            reason_code=ExpansionReasonCode.HUMAN_EXPANSION_INTENT,
        )
    )
    for identifier, ref in (
        ("exp_process_purpose", "target_process.purpose"),
        ("exp_process_risk", "target_process.risk"),
        ("exp_process_outcome", "target_process.expected_outcomes"),
    ):
        items.append(
            ExpansionPlanItem(
                id=identifier,
                subject_kind=ExpansionSubjectKind.PROCESS_VALUE,
                subject_ref=ref,
                source_id=request.target_process_id,
                disposition=ExpansionDisposition.ASK_HUMAN,
                reason_code=ExpansionReasonCode.NEW_PROCESS_SPECIFIC_CONTEXT,
            )
        )

    # Role and preconditions are reusable only when their existing authority is strong
    # enough. They still remain explicit items so the operator can see the inheritance.
    items.append(
        _knowledge_item(
            "exp_process_role",
            ExpansionSubjectKind.PROCESS_VALUE,
            "target_process.role",
            base_context.process.id,
            base_context.process.role,
        )
    )
    for index, value in enumerate(base_context.process.preconditions, start=1):
        items.append(
            _knowledge_item(
                f"exp_process_precondition_{index:02d}",
                ExpansionSubjectKind.PROCESS_VALUE,
                f"target_process.preconditions[{index - 1}]",
                base_context.process.id,
                value,
            )
        )

    items.append(
        ExpansionPlanItem(
            id="exp_framework_snapshot",
            subject_kind=ExpansionSubjectKind.FRAMEWORK_SNAPSHOT,
            subject_ref="framework.snapshot",
            source_id=snapshot.id,
            disposition=ExpansionDisposition.REUSE,
            reason_code=ExpansionReasonCode.FRAMEWORK_SNAPSHOT_BOUND,
        )
    )

    counts = {disposition: 0 for disposition in ExpansionDisposition}
    for item in items:
        counts[item.disposition] += 1
    status = (
        ExpansionPlanStatus.BLOCKED
        if counts[ExpansionDisposition.BLOCKED]
        else ExpansionPlanStatus.READY_FOR_REVIEW
    )
    return ExpansionPlan(
        id=plan_id,
        request_id=request.id,
        base_context_id=base_context.id,
        base_context_sha256=request.base_context_sha256,
        workspace_profile_id=request.workspace_profile_id,
        framework_snapshot_id=snapshot.id,
        framework_snapshot_fingerprint=snapshot.root_fingerprint,
        created_at=created_at,
        status=status,
        items=tuple(items),
        reuse_count=counts[ExpansionDisposition.REUSE],
        ask_human_count=counts[ExpansionDisposition.ASK_HUMAN],
        observe_new_count=counts[ExpansionDisposition.OBSERVE_NEW],
        reobserve_count=counts[ExpansionDisposition.REOBSERVE],
        review_count=counts[ExpansionDisposition.REVIEW],
        blocked_count=counts[ExpansionDisposition.BLOCKED],
    )


def _validate_bindings(
    request: ExpansionRequest,
    base_context: ContextBundle,
    snapshot: FrameworkSnapshot,
    inventory: ObservationInventory | None,
    report: FrontendChangeReport | None,
) -> None:
    if request.base_context_id != base_context.id:
        raise ValueError("expansion request does not belong to supplied base context")
    if request.base_context_sha256 != context_sha256(base_context):
        raise ValueError("base context fingerprint changed after expansion request")
    if request.framework_snapshot_id != snapshot.id:
        raise ValueError("expansion request does not belong to supplied framework snapshot")
    if request.framework_snapshot_fingerprint != snapshot.root_fingerprint:
        raise ValueError("framework fingerprint changed after expansion request")
    if request.workspace_profile_id != snapshot.profile_id:
        raise ValueError("expansion request workspace profile does not match snapshot")
    if inventory is not None:
        if inventory.context_bundle_id != base_context.id:
            raise ValueError("observation inventory does not belong to base context")
        known = {item.element_id for item in inventory.items} | {item.id for item in base_context.elements}
        missing = sorted(set(request.target_element_ids) - known)
        if missing:
            raise ValueError(f"requested expansion targets are not mapped: {missing}")
    elif not set(request.target_element_ids).issubset({item.id for item in base_context.elements}):
        raise ValueError("targets outside base context require an accepted observation inventory")
    if request.proactive_report_id is not None:
        if report is None or report.id != request.proactive_report_id:
            raise ValueError("expansion request requires the referenced proactive report")
    if report is not None and inventory is not None and report.inventory_id != inventory.id:
        raise ValueError("proactive report does not belong to supplied observation inventory")


def _target_page_ids(
    request: ExpansionRequest,
    context: ContextBundle,
    inventory: ObservationInventory | None,
) -> set[str]:
    page_ids: set[str] = set()
    element_by_id = {item.id: item for item in context.elements}
    component_owner_page = {
        component.id: page.id
        for page in context.pages
        for component in context.components
        if component.id in page.component_ids
    }
    inventory_by_element = {} if inventory is None else {item.element_id: item for item in inventory.items}
    page_id_set = {page.id for page in context.pages}
    for element_id in request.target_element_ids:
        element = element_by_id.get(element_id)
        if element is not None:
            if element.owner_id in page_id_set:
                page_ids.add(element.owner_id)
            elif element.owner_id in component_owner_page:
                page_ids.add(component_owner_page[element.owner_id])
            continue
        mapped = inventory_by_element.get(element_id)
        if mapped is not None:
            page_ids.add(mapped.page_id)
    return page_ids


def _knowledge_item(
    item_id: str,
    subject_kind: ExpansionSubjectKind,
    subject_ref: str,
    source_id: str,
    value: KnowledgeText,
) -> ExpansionPlanItem:
    disposition, reason = _knowledge_disposition(value.status)
    return ExpansionPlanItem(
        id=item_id,
        subject_kind=subject_kind,
        subject_ref=subject_ref,
        source_id=source_id,
        knowledge_status=value.status,
        disposition=disposition,
        reason_code=reason,
        evidence_ids=value.evidence_ids,
    )


def _knowledge_disposition(status: KnowledgeStatus) -> tuple[ExpansionDisposition, ExpansionReasonCode]:
    if status in {KnowledgeStatus.CONFIRMED, KnowledgeStatus.OBSERVED}:
        return ExpansionDisposition.REUSE, ExpansionReasonCode.AUTHORIZED_CURRENT_KNOWLEDGE
    if status is KnowledgeStatus.UNKNOWN:
        return ExpansionDisposition.ASK_HUMAN, ExpansionReasonCode.NEW_PROCESS_SPECIFIC_CONTEXT
    if status is KnowledgeStatus.STALE:
        return ExpansionDisposition.REOBSERVE, ExpansionReasonCode.KNOWLEDGE_REQUIRES_REOBSERVATION
    if status is KnowledgeStatus.CONFLICTING:
        return ExpansionDisposition.BLOCKED, ExpansionReasonCode.KNOWLEDGE_CONFLICT
    return ExpansionDisposition.REVIEW, ExpansionReasonCode.KNOWLEDGE_REQUIRES_REVIEW


def _target_element_item(*, item_id, element_id, base_element, mapped, observation):
    if observation is not None:
        if observation.disposition is ChangeDisposition.LOCATOR_DRIFT:
            return ExpansionPlanItem(
                id=item_id,
                subject_kind=ExpansionSubjectKind.ELEMENT,
                subject_ref=f"elements.{element_id}",
                source_id=element_id,
                disposition=ExpansionDisposition.REOBSERVE,
                reason_code=ExpansionReasonCode.PROACTIVE_LOCATOR_DRIFT,
            )
        if observation.disposition is ChangeDisposition.MISSING:
            return ExpansionPlanItem(
                id=item_id,
                subject_kind=ExpansionSubjectKind.ELEMENT,
                subject_ref=f"elements.{element_id}",
                source_id=element_id,
                disposition=ExpansionDisposition.BLOCKED,
                reason_code=ExpansionReasonCode.PROACTIVE_TARGET_MISSING,
            )
        if observation.disposition is ChangeDisposition.AMBIGUOUS:
            return ExpansionPlanItem(
                id=item_id,
                subject_kind=ExpansionSubjectKind.ELEMENT,
                subject_ref=f"elements.{element_id}",
                source_id=element_id,
                disposition=ExpansionDisposition.REVIEW,
                reason_code=ExpansionReasonCode.PROACTIVE_TARGET_AMBIGUOUS,
            )
    if base_element is None:
        if mapped is None:
            raise ValueError(f"target element is not mapped: {element_id}")
        return ExpansionPlanItem(
            id=item_id,
            subject_kind=ExpansionSubjectKind.ELEMENT,
            subject_ref=f"elements.{element_id}",
            source_id=element_id,
            disposition=ExpansionDisposition.OBSERVE_NEW,
            reason_code=ExpansionReasonCode.TARGET_NOT_IN_BASE_CONTEXT,
        )
    primary = next((item for item in base_element.locator_candidates if item.primary), None)
    if primary is None:
        return ExpansionPlanItem(
            id=item_id,
            subject_kind=ExpansionSubjectKind.ELEMENT,
            subject_ref=f"elements.{element_id}",
            source_id=element_id,
            disposition=ExpansionDisposition.BLOCKED,
            reason_code=ExpansionReasonCode.KNOWLEDGE_CONFLICT,
        )
    disposition, reason = _knowledge_disposition(primary.value.status)
    return ExpansionPlanItem(
        id=item_id,
        subject_kind=ExpansionSubjectKind.ELEMENT,
        subject_ref=f"elements.{element_id}",
        source_id=element_id,
        knowledge_status=primary.value.status,
        disposition=disposition,
        reason_code=reason,
        evidence_ids=tuple(dict.fromkeys((*base_element.name.evidence_ids, *base_element.semantic_role.evidence_ids, *primary.value.evidence_ids))),
    )
