import json

import pytest

from test_cartographer.discovery.models import DiscoveryAmbiguity
from test_cartographer.discovery.parser import DiscoveryOutputError, parse_ambiguity_question


@pytest.fixture
def ambiguity() -> DiscoveryAmbiguity:
    return DiscoveryAmbiguity(
        id="amb_target_search_submit",
        target_id="target_search_submit",
        candidate_ids=("cand_002", "cand_003"),
    )


def test_parser_preserves_candidate_set(ambiguity) -> None:
    raw = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": ambiguity.id,
            "candidate_ids": list(ambiguity.candidate_ids),
            "user_prompt": "Which Search button submits the catalog form?",
            "reason": "Both visible controls have the same role and name.",
        }
    )
    result = parse_ambiguity_question(raw, ambiguity)
    assert result.candidate_ids == ambiguity.candidate_ids


def test_parser_rejects_model_selection(ambiguity) -> None:
    raw = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": ambiguity.id,
            "candidate_ids": ["cand_002"],
            "user_prompt": "Use cand_002.",
            "reason": "I selected it.",
        }
    )
    with pytest.raises(DiscoveryOutputError):
        parse_ambiguity_question(raw, ambiguity)


def test_parser_rejects_secret_request(ambiguity) -> None:
    raw = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": ambiguity.id,
            "candidate_ids": list(ambiguity.candidate_ids),
            "user_prompt": "Which candidate is correct, and what password is used?",
            "reason": "Need a password.",
        }
    )
    with pytest.raises(DiscoveryOutputError, match="prohibited"):
        parse_ambiguity_question(raw, ambiguity)


def test_parser_rejects_explicit_candidate_recommendation(ambiguity) -> None:
    raw = json.dumps(
        {
            "schema_version": "0.1",
            "ambiguity_id": ambiguity.id,
            "candidate_ids": list(ambiguity.candidate_ids),
            "user_prompt": "Which candidate matches the intended action?",
            "reason": "The correct candidate is cand_002.",
        }
    )
    with pytest.raises(DiscoveryOutputError, match="select a candidate"):
        parse_ambiguity_question(raw, ambiguity)
