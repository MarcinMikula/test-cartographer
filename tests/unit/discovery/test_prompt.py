from test_cartographer.discovery.models import DiscoveryAmbiguity
from test_cartographer.discovery.prompt import ambiguity_json_schema, build_ambiguity_prompt


def test_prompt_contains_only_bounded_candidate_descriptors(plan, candidates) -> None:
    ambiguity = DiscoveryAmbiguity(
        id="amb_target_search_submit",
        target_id="target_search_submit",
        candidate_ids=("cand_002", "cand_003"),
    )
    target = next(item for item in plan.targets if item.id == ambiguity.target_id)
    prompt = build_ambiguity_prompt(ambiguity, target, candidates)
    assert "search-submit" in prompt
    assert "search-help" in prompt
    assert "do-not-persist" not in prompt
    assert plan.source_url not in prompt


def test_schema_preserves_exact_candidate_set() -> None:
    ambiguity = DiscoveryAmbiguity(
        id="amb_target_search_submit",
        target_id="target_search_submit",
        candidate_ids=("cand_002", "cand_003"),
    )
    schema = ambiguity_json_schema(ambiguity)
    assert schema["properties"]["ambiguity_id"]["const"] == ambiguity.id
    assert schema["properties"]["candidate_ids"]["items"]["enum"] == [
        "cand_002",
        "cand_003",
    ]
