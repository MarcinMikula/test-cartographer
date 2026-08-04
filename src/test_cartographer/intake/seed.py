"""Build a structurally valid context skeleton from one minimal human request."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Literal

from test_cartographer.context.enums import (
    ActionKind,
    EvidenceSourceType,
    KnowledgeStatus,
    LocatorStrategy,
    SensitivityLevel,
)
from test_cartographer.context.models import (
    ApplicationContext,
    ContextBundle,
    ContractModel,
    Evidence,
    ExpectedOutcome,
    Identifier,
    KnowledgeText,
    LocatorCandidate,
    NonEmptyText,
    PageContext,
    ProcessContext,
    ProcessStep,
    UIAction,
    UIElement,
)


class MinimalContextSeed(ContractModel):
    """The smallest persisted input accepted before guided intake begins."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    context_id: Identifier
    title: NonEmptyText
    initial_request: NonEmptyText
    created_at: datetime
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL


def build_minimal_context(seed: MinimalContextSeed) -> ContextBundle:
    """Create an honest unknown-heavy skeleton without inventing app facts."""

    if seed.created_at.tzinfo is None or seed.created_at.utcoffset() is None:
        raise ValueError("seed created_at must include a timezone offset")

    evidence = Evidence(
        id="ev_initial_request",
        source_type=EvidenceSourceType.HUMAN,
        source_ref=f"guided_intake_seed:{seed.id}",
        summary="A human supplied the initial automation request.",
        captured_at=seed.created_at,
        sensitivity=seed.sensitivity,
        content_sha256=hashlib.sha256(seed.initial_request.encode("utf-8")).hexdigest(),
    )
    unknown = lambda sensitivity=SensitivityLevel.INTERNAL: KnowledgeText(
        value=None,
        status=KnowledgeStatus.UNKNOWN,
        evidence_ids=(),
        confidence=None,
        sensitivity=sensitivity,
    )
    request_intent = KnowledgeText(
        value=seed.initial_request,
        status=KnowledgeStatus.PROVIDED,
        evidence_ids=(evidence.id,),
        sensitivity=seed.sensitivity,
        notes="Initial request only; detailed process discovery is still required.",
    )

    application = ApplicationContext(
        id="app_target",
        name=unknown(),
        environment=unknown(),
        base_url=unknown(SensitivityLevel.CONFIDENTIAL),
    )
    placeholder_element = UIElement(
        id="el_discovery_target",
        owner_id="page_discovery_target",
        name=unknown(),
        semantic_role=unknown(),
        locator_candidates=(
            LocatorCandidate(
                id="loc_discovery_target",
                strategy=LocatorStrategy.CSS,
                value=unknown(),
                primary=False,
            ),
        ),
    )
    page = PageContext(
        id="page_discovery_target",
        name=unknown(),
        route=unknown(SensitivityLevel.CONFIDENTIAL),
        element_ids=(placeholder_element.id,),
    )
    process = ProcessContext(
        id="proc_target",
        name=unknown(),
        purpose=unknown(),
        risk=unknown(),
        role=unknown(),
        preconditions=(unknown(),),
        steps=(
            ProcessStep(
                id="step_begin_discovery",
                order=1,
                page_id=page.id,
                intent=request_intent,
                action=UIAction(kind=ActionKind.NAVIGATE),
                expected_state=unknown(),
            ),
        ),
        expected_outcomes=(
            ExpectedOutcome(
                id="outcome_target",
                statement=unknown(),
                related_element_ids=(placeholder_element.id,),
            ),
        ),
    )
    return ContextBundle(
        id=seed.context_id,
        title=seed.title,
        created_at=seed.created_at,
        updated_at=seed.created_at,
        application=application,
        process=process,
        pages=(page,),
        elements=(placeholder_element,),
        evidence=(evidence,),
    )
