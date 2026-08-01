"""Human review and context application for bounded browser observations."""

from __future__ import annotations

import hashlib
from datetime import datetime

from test_cartographer.context.enums import EvidenceSourceType, KnowledgeStatus
from test_cartographer.context.models import ContextBundle, Evidence, KnowledgeText
from test_cartographer.observation.enums import ObservationDecision
from test_cartographer.observation.models import BrowserObservation


def review_observation(
    observation: BrowserObservation,
    *,
    decision: ObservationDecision,
    reviewed_at: datetime,
    reason: str | None = None,
    review_seconds: float = 0.0,
) -> BrowserObservation:
    """Record one final human acceptance or rejection."""

    if observation.decision is not ObservationDecision.PENDING:
        raise ValueError("observation has already been reviewed")
    if decision is ObservationDecision.PENDING:
        raise ValueError("review decision must be accepted or rejected")
    updated = observation.model_copy(
        update={
            "decision": decision,
            "reviewed_at": reviewed_at,
            "review_reason": reason,
            "review_seconds": review_seconds,
        }
    )
    return BrowserObservation.model_validate(updated.model_dump(mode="python"))


def apply_accepted_observation(
    context: ContextBundle,
    observation: BrowserObservation,
) -> ContextBundle:
    """Promote only the verified primary locator and append application evidence."""

    if observation.decision is not ObservationDecision.ACCEPTED:
        raise ValueError("only an accepted observation can update context")
    if observation.reviewed_at is None:  # defensive; model already guarantees this
        raise ValueError("accepted observation requires reviewed_at")
    if observation.context_id != context.id:
        raise ValueError("observation context_id does not match context")

    evidence_id = _evidence_id(observation.id)
    if any(item.id == evidence_id for item in context.evidence):
        raise ValueError(f"observation evidence already exists: {evidence_id}")

    target_found = False
    updated_elements = []
    for element in context.elements:
        if element.id != observation.target_element_id:
            updated_elements.append(element)
            continue
        updated_locators = []
        for locator in element.locator_candidates:
            if locator.id != observation.target_locator_id:
                updated_locators.append(locator)
                continue
            if not locator.primary:
                raise ValueError("observation target must remain the primary locator")
            if locator.strategy is not observation.locator.strategy:
                raise ValueError("observation locator strategy does not match context")
            if locator.value.value != observation.locator.value:
                raise ValueError("observation locator value does not match context")
            evidence_ids = tuple(dict.fromkeys((*locator.value.evidence_ids, evidence_id)))
            observed_value = KnowledgeText(
                value=locator.value.value,
                status=KnowledgeStatus.OBSERVED,
                evidence_ids=evidence_ids,
                confidence=None,
                sensitivity=locator.value.sensitivity,
                notes="Verified by an accepted bounded browser observation.",
            )
            updated_locators.append(locator.model_copy(update={"value": observed_value}))
            target_found = True
        updated_elements.append(
            element.model_copy(update={"locator_candidates": tuple(updated_locators)})
        )

    if not target_found:
        raise ValueError("observation target element or locator was not found in context")

    evidence = Evidence(
        id=evidence_id,
        source_type=EvidenceSourceType.APPLICATION,
        source_ref=f"browser_observation:{observation.id}",
        summary=(
            f"Accepted bounded observation for element "
            f"{observation.target_element_id} using locator "
            f"{observation.target_locator_id}."
        ),
        captured_at=observation.captured_at,
        sensitivity=observation.sensitivity,
        content_sha256=observation.capture_sha256,
    )
    updated = context.model_copy(
        update={
            "updated_at": observation.reviewed_at,
            "elements": tuple(updated_elements),
            "evidence": (*context.evidence, evidence),
        }
    )
    return ContextBundle.model_validate(updated.model_dump(mode="python"))


def _evidence_id(observation_id: str) -> str:
    digest = hashlib.sha256(observation_id.encode("utf-8")).hexdigest()[:16]
    return f"ev_browser_{digest}"
