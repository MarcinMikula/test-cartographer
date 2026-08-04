"""Strict parser and authority checks for ambiguity-question output."""

from __future__ import annotations

import json

from pydantic import ValidationError

from test_cartographer.discovery.models import AmbiguityQuestionPlan, DiscoveryAmbiguity

_PROHIBITED = (
    "password",
    "credential",
    "token",
    "cookie",
    "secret",
    "api key",
    "input value",
)
_SELECTION_PHRASES = (
    "correct candidate is",
    "best candidate is",
    "use cand_",
    "select cand_",
    "choose cand_",
    "pick cand_",
)


class DiscoveryOutputError(ValueError):
    pass


def parse_ambiguity_question(
    raw: str,
    ambiguity: DiscoveryAmbiguity,
) -> AmbiguityQuestionPlan:
    if raw.strip().startswith("```"):
        raise DiscoveryOutputError("Markdown fences are not allowed")
    try:
        data = json.loads(raw, object_pairs_hook=_reject_duplicates)
        plan = AmbiguityQuestionPlan.model_validate(data)
    except (json.JSONDecodeError, ValidationError, DiscoveryOutputError) as exc:
        raise DiscoveryOutputError("invalid discovery ambiguity output") from exc
    if plan.ambiguity_id != ambiguity.id:
        raise DiscoveryOutputError("ambiguity ID changed")
    if (
        len(plan.candidate_ids) != len(ambiguity.candidate_ids)
        or set(plan.candidate_ids) != set(ambiguity.candidate_ids)
    ):
        raise DiscoveryOutputError("candidate set changed")
    combined = f"{plan.user_prompt} {plan.reason}".casefold()
    if any(term in combined for term in _PROHIBITED):
        raise DiscoveryOutputError("discovery question requests prohibited information")
    if any(term in combined for term in _SELECTION_PHRASES):
        raise DiscoveryOutputError("model attempted to select a candidate")
    return plan


def _reject_duplicates(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DiscoveryOutputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result
