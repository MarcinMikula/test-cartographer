from test_cartographer.discovery.enums import DiscoveryTargetState, SelectionAuthority
from test_cartographer.discovery.ranking import rank_targets


def test_unique_targets_are_selected_deterministically(plan, candidates, profile) -> None:
    results = rank_targets(plan.targets, candidates, profile)
    assert results[0].state is DiscoveryTargetState.SELECTED
    assert results[0].selected_candidate_id == "cand_001"
    assert results[0].selection_authority is SelectionAuthority.DETERMINISTIC
    assert results[2].selected_candidate_id == "cand_004"


def test_equal_search_buttons_create_ambiguity(plan, candidates, profile) -> None:
    result = rank_targets(plan.targets, candidates, profile)[1]
    assert result.state is DiscoveryTargetState.AMBIGUOUS
    assert tuple(item.candidate_id for item in result.ranked_candidates[:2]) == (
        "cand_002",
        "cand_003",
    )
    assert result.ranked_candidates[0].score == result.ranked_candidates[1].score
