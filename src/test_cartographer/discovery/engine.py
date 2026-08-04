"""Guidance, human resolution, and review transitions for discovery."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from test_cartographer.discovery.enums import (
    DiscoveryDecision,
    DiscoveryProviderKind,
    DiscoveryRunState,
    DiscoveryTargetState,
    SelectionAuthority,
)
from test_cartographer.discovery.models import (
    AmbiguityQuestionPlan,
    DiscoveryGuidanceTurn,
    DiscoveryProfile,
    DiscoveryTarget,
    ProcessDiscoveryRun,
)
from test_cartographer.discovery.parser import parse_ambiguity_question
from test_cartographer.discovery.prompt import build_ambiguity_prompt
from test_cartographer.discovery.provider import DiscoveryQuestionProvider


def phrase_ambiguity(
    run: ProcessDiscoveryRun,
    targets: tuple[DiscoveryTarget, ...],
    profile: DiscoveryProfile,
    provider: DiscoveryQuestionProvider,
    *,
    ambiguity_id: str,
    started_at: datetime,
    completed_at: datetime | None,
) -> tuple[AmbiguityQuestionPlan, ProcessDiscoveryRun]:
    ambiguity = next((item for item in run.ambiguities if item.id == ambiguity_id), None)
    if ambiguity is None:
        raise ValueError(f"unknown ambiguity: {ambiguity_id}")
    if ambiguity.selected_candidate_id is not None:
        raise ValueError("ambiguity is already resolved")
    target = next(item for item in targets if item.id == ambiguity.target_id)
    prompt = build_ambiguity_prompt(ambiguity, target, run.candidates)
    result = provider.phrase(ambiguity, prompt)
    actual_completed_at = completed_at or datetime.now(timezone.utc)
    plan = parse_ambiguity_question(result.raw_output, ambiguity)
    provider_kind = (
        DiscoveryProviderKind.OLLAMA
        if profile.provider is DiscoveryProviderKind.OLLAMA
        else DiscoveryProviderKind.REPLAY
    )
    turn = DiscoveryGuidanceTurn(
        sequence=len(run.guidance_turns) + 1,
        ambiguity_id=ambiguity.id,
        provider=provider_kind,
        model=result.model,
        candidate_ids=ambiguity.candidate_ids,
        started_at=started_at,
        completed_at=actual_completed_at,
        latency_seconds=result.latency_seconds,
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        response_sha256=hashlib.sha256(result.raw_output.encode("utf-8")).hexdigest(),
        prompt_characters=len(prompt),
        response_characters=len(result.raw_output),
    )
    updated_ambiguities = tuple(
        item.model_copy(update={"question": plan.user_prompt})
        if item.id == ambiguity.id
        else item
        for item in run.ambiguities
    )
    updated = run.model_copy(
        update={
            "ambiguities": updated_ambiguities,
            "guidance_turns": (*run.guidance_turns, turn),
            "updated_at": actual_completed_at,
            "live_provider_used": run.live_provider_used
            or provider_kind is DiscoveryProviderKind.OLLAMA,
        }
    )
    return plan, ProcessDiscoveryRun.model_validate(updated.model_dump(mode="python"))


def resolve_ambiguity(
    run: ProcessDiscoveryRun,
    *,
    ambiguity_id: str,
    selected_candidate_id: str,
    resolved_at: datetime,
    reason: str,
) -> ProcessDiscoveryRun:
    ambiguity = next((item for item in run.ambiguities if item.id == ambiguity_id), None)
    if ambiguity is None:
        raise ValueError(f"unknown ambiguity: {ambiguity_id}")
    if ambiguity.question is None:
        raise ValueError("ambiguity must be phrased before human resolution")
    resolved = ambiguity.model_copy(
        update={
            "selected_candidate_id": selected_candidate_id,
            "resolved_at": resolved_at,
            "resolution_reason": reason,
        }
    )
    targets = tuple(
        target.model_copy(
            update={
                "state": DiscoveryTargetState.SELECTED,
                "selected_candidate_id": selected_candidate_id,
                "selection_authority": SelectionAuthority.HUMAN,
            }
        )
        if target.target_id == ambiguity.target_id
        else target
        for target in run.targets
    )
    ambiguities = tuple(resolved if item.id == ambiguity_id else item for item in run.ambiguities)
    unresolved = any(item.selected_candidate_id is None for item in ambiguities)
    missing = any(item.state is DiscoveryTargetState.MISSING for item in targets)
    state = DiscoveryRunState.AWAITING_RESOLUTION if unresolved or missing else DiscoveryRunState.RESOLVED
    updated = run.model_copy(
        update={
            "targets": targets,
            "ambiguities": ambiguities,
            "state": state,
            "updated_at": resolved_at,
        }
    )
    return ProcessDiscoveryRun.model_validate(updated.model_dump(mode="python"))


def review_discovery(
    run: ProcessDiscoveryRun,
    *,
    decision: DiscoveryDecision,
    reviewed_at: datetime,
    reason: str | None = None,
    review_seconds: float = 0.0,
) -> ProcessDiscoveryRun:
    if run.decision is not DiscoveryDecision.PENDING:
        raise ValueError("discovery has already been reviewed")
    if decision is DiscoveryDecision.PENDING:
        raise ValueError("review decision must be accepted or rejected")
    if decision is DiscoveryDecision.ACCEPTED and run.state is not DiscoveryRunState.RESOLVED:
        raise ValueError("only a fully resolved discovery may be accepted")
    updated = run.model_copy(
        update={
            "decision": decision,
            "state": (
                DiscoveryRunState.ACCEPTED
                if decision is DiscoveryDecision.ACCEPTED
                else DiscoveryRunState.REJECTED
            ),
            "reviewed_at": reviewed_at,
            "review_reason": reason,
            "review_seconds": review_seconds,
            "updated_at": reviewed_at,
        }
    )
    return ProcessDiscoveryRun.model_validate(updated.model_dump(mode="python"))
