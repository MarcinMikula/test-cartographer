"""Minimized prompt and JSON Schema for ambiguity-question phrasing."""

from __future__ import annotations

from test_cartographer.discovery.models import (
    DiscoveryAmbiguity,
    DiscoveryTarget,
    ElementCandidate,
)


def build_ambiguity_prompt(
    ambiguity: DiscoveryAmbiguity,
    target: DiscoveryTarget,
    candidates: tuple[ElementCandidate, ...],
) -> str:
    by_id = {candidate.id: candidate for candidate in candidates}
    lines = [
        "You are phrasing one bounded clarification question for UI discovery.",
        "Do not choose a candidate. Do not request credentials, tokens, cookies, or input values.",
        f"Ambiguity ID: {ambiguity.id}",
        f"Target: {target.name}",
        f"Action: {target.action_kind.value}",
        "Allowed candidates:",
    ]
    for candidate_id in ambiguity.candidate_ids:
        candidate = by_id[candidate_id]
        attrs = ", ".join(f"{item.name}={item.value}" for item in candidate.attributes) or "none"
        locators = ", ".join(
            f"{item.strategy.value}={item.value} (matches={item.match_count})"
            for item in candidate.locator_candidates
        )
        lines.append(
            f"- {candidate.id}: tag={candidate.tag_name}; role={candidate.semantic_role}; "
            f"name={candidate.semantic_name}; attributes={attrs}; locators={locators}"
        )
    lines.extend(
        (
            "Return one JSON object matching the supplied schema.",
            "Preserve the ambiguity ID and every candidate ID exactly.",
            "Ask the human which candidate represents the intended process step.",
        )
    )
    return "\n".join(lines)


def ambiguity_json_schema(ambiguity: DiscoveryAmbiguity) -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "ambiguity_id", "candidate_ids", "user_prompt", "reason"],
        "properties": {
            "schema_version": {"type": "string", "const": "0.1"},
            "ambiguity_id": {"type": "string", "const": ambiguity.id},
            "candidate_ids": {
                "type": "array",
                "minItems": len(ambiguity.candidate_ids),
                "maxItems": len(ambiguity.candidate_ids),
                "uniqueItems": True,
                "items": {"type": "string", "enum": list(ambiguity.candidate_ids)},
            },
            "user_prompt": {"type": "string", "minLength": 1, "maxLength": 320},
            "reason": {"type": "string", "minLength": 1, "maxLength": 240},
        },
    }
