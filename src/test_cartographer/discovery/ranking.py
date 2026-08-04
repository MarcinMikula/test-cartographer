"""Deterministic candidate ranking for one bounded discovery plan."""

from __future__ import annotations

import re

from test_cartographer.context.enums import ActionKind
from test_cartographer.discovery.enums import (
    DiscoveryTargetState,
    SelectionAuthority,
)
from test_cartographer.discovery.models import (
    CandidateScore,
    DiscoveryProfile,
    DiscoveryTarget,
    DiscoveryTargetResult,
    ElementCandidate,
)

_TOKEN = re.compile(r"[a-z0-9]+")


def rank_targets(
    targets: tuple[DiscoveryTarget, ...],
    candidates: tuple[ElementCandidate, ...],
    profile: DiscoveryProfile,
) -> tuple[DiscoveryTargetResult, ...]:
    return tuple(_rank_target(target, candidates, profile) for target in targets)


def _rank_target(
    target: DiscoveryTarget,
    candidates: tuple[ElementCandidate, ...],
    profile: DiscoveryProfile,
) -> DiscoveryTargetResult:
    scored = sorted(
        (_score(target, candidate) for candidate in candidates),
        key=lambda item: (-item.score, item.candidate_id),
    )[: profile.max_candidates_per_target]
    usable = [item for item in scored if item.score >= profile.minimum_candidate_score]
    if not usable:
        return DiscoveryTargetResult(
            target_id=target.id,
            state=DiscoveryTargetState.MISSING,
            ranked_candidates=tuple(scored),
        )
    if len(usable) >= 2 and usable[0].score - usable[1].score <= profile.ambiguity_score_delta:
        return DiscoveryTargetResult(
            target_id=target.id,
            state=DiscoveryTargetState.AMBIGUOUS,
            ranked_candidates=tuple(usable),
        )
    return DiscoveryTargetResult(
        target_id=target.id,
        state=DiscoveryTargetState.SELECTED,
        ranked_candidates=tuple(usable),
        selected_candidate_id=usable[0].candidate_id,
        selection_authority=SelectionAuthority.DETERMINISTIC,
    )


def _score(target: DiscoveryTarget, candidate: ElementCandidate) -> CandidateScore:
    target_tokens = _tokens(target.name, *target.expected_roles)
    values = [candidate.semantic_name, candidate.semantic_role, candidate.tag_name]
    values.extend(item.value for item in candidate.attributes)
    candidate_tokens = _tokens(*values)
    matched = tuple(sorted(target_tokens & candidate_tokens))
    score = min(40, len(matched) * 10)
    if candidate.semantic_role in target.expected_roles:
        score += 35
    if _action_compatible(target.action_kind, candidate):
        score += 15
    if any(locator.match_count == 1 for locator in candidate.locator_candidates):
        score += 10
    return CandidateScore(
        candidate_id=candidate.id,
        score=min(100, score),
        matched_tokens=matched,
    )


def _action_compatible(action: ActionKind, candidate: ElementCandidate) -> bool:
    if action is ActionKind.FILL:
        return candidate.editable and candidate.tag_name in {"input", "textarea"}
    if action is ActionKind.SELECT:
        return candidate.editable and candidate.tag_name == "select"
    if action is ActionKind.CLICK:
        return candidate.enabled and candidate.semantic_role in {"button", "link", "checkbox"}
    if action is ActionKind.READ:
        return candidate.semantic_role in {"list", "table", "status", "heading"}
    if action in {ActionKind.CHECK, ActionKind.UNCHECK}:
        return candidate.semantic_role == "checkbox"
    return False


def _tokens(*values: str) -> set[str]:
    return {
        token
        for value in values
        for token in _TOKEN.findall(value.casefold())
        if len(token) > 1
    }
