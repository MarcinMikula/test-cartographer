"""Human confirmation bridge between discovery readiness and synthesis authority."""

from __future__ import annotations

import hashlib
from datetime import datetime

from test_cartographer.context.enums import ActionKind, EvidenceSourceType, KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import (
    ApplicationContext,
    ContextBundle,
    Evidence,
    KnowledgeText,
    ProcessContext,
)


HANDOFF_PATHS = (
    "application.name",
    "application.environment",
    "process.name",
    "process.steps[opening_navigation].intent",
)


def confirm_synthesis_handoff(
    context: ContextBundle,
    *,
    confirmed_at: datetime,
) -> ContextBundle:
    """Confirm every remaining human-provided value required by synthesis."""

    evidence_id = "ev_creation_handoff"
    evidence = Evidence(
        id=evidence_id,
        source_type=EvidenceSourceType.HUMAN,
        source_ref="creation_flow:synthesis_handoff_review",
        summary=(
            "Human confirmed application identity, environment, process name, "
            "and the inherited opening-step intent for synthesis."
        ),
        captured_at=confirmed_at,
        sensitivity=SensitivityLevel.INTERNAL,
        content_sha256=hashlib.sha256("|".join(HANDOFF_PATHS).encode("utf-8")).hexdigest(),
    )

    def confirm(value: KnowledgeText, *, path: str) -> KnowledgeText:
        if value.value is None:
            raise ValueError(f"synthesis handoff cannot confirm an empty value: {path}")
        if value.status is not KnowledgeStatus.PROVIDED:
            raise ValueError(
                f"synthesis handoff expects a human-provided value at {path}; "
                f"found {value.status.value}"
            )
        return value.model_copy(
            update={
                "status": KnowledgeStatus.CONFIRMED,
                "evidence_ids": tuple(dict.fromkeys((*value.evidence_ids, evidence_id))),
                "confidence": None,
            }
        )

    navigation_steps = tuple(
        step
        for step in context.process.steps
        if step.action.kind is ActionKind.NAVIGATE
    )
    discovered_steps = tuple(
        step
        for step in context.process.steps
        if step.action.kind is not ActionKind.NAVIGATE
    )
    if len(navigation_steps) != 1 or not discovered_steps:
        raise ValueError(
            "synthesis handoff requires one opening navigation and discovered process steps"
        )
    opening_step = navigation_steps[0]
    updated_steps = []
    for step in context.process.steps:
        if step.id == opening_step.id:
            step = step.model_copy(
                update={
                    "intent": confirm(
                        step.intent,
                        path="process.steps[opening_navigation].intent",
                    )
                }
            )
        updated_steps.append(step)

    application = ApplicationContext(
        id=context.application.id,
        name=confirm(context.application.name, path="application.name"),
        environment=confirm(
            context.application.environment,
            path="application.environment",
        ),
        base_url=context.application.base_url,
    )
    process = ProcessContext(
        id=context.process.id,
        name=confirm(context.process.name, path="process.name"),
        purpose=context.process.purpose,
        risk=context.process.risk,
        role=context.process.role,
        preconditions=context.process.preconditions,
        steps=tuple(updated_steps),
        expected_outcomes=context.process.expected_outcomes,
    )
    updated = context.model_copy(
        update={
            "updated_at": confirmed_at,
            "application": application,
            "process": process,
            "evidence": (*context.evidence, evidence),
        }
    )
    return ContextBundle.model_validate(updated.model_dump(mode="python"))
