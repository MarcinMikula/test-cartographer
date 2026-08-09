import pytest

from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.expansion.context_builder import (
    build_candidate_expansion_context,
    observed_element_from_regression,
)
from test_cartographer.proactive_regression.enums import ChangeDisposition


def test_candidate_uses_current_reobserved_sort_locator(candidate_context):
    sort = next(item for item in candidate_context.elements if item.id == "el_sort_results")
    locator = sort.locator_candidates[0]
    assert locator.value.value == "catalog-sort-control"
    assert locator.value.status is KnowledgeStatus.OBSERVED


def test_candidate_reuses_required_existing_results_element(candidate_context):
    assert {item.id for item in candidate_context.elements} == {
        "el_results_list",
        "el_sort_results",
    }


def test_candidate_construction_does_not_mutate_base_context(base_context, candidate_context):
    assert base_context.process.id == "proc_search_catalog"
    assert {item.id for item in base_context.elements} == {"el_results_list"}
    assert candidate_context.process.id == "proc_sort_catalog"


def test_reobserve_target_requires_fresh_observation(
    expansion_request,
    accepted_expansion_plan,
    base_context,
    target_process,
    fixed_now,
):
    with pytest.raises(ValueError, match="requires fresh observation"):
        build_candidate_expansion_context(
            expansion_request,
            accepted_expansion_plan,
            base_context,
            target_process,
            candidate_context_id="ctx_missing_fresh",
            title="Missing fresh evidence",
            created_at=fixed_now,
        )


def test_missing_regression_target_cannot_become_observed_context(
    observation_inventory,
    drift_observation,
    fixed_now,
):
    missing = drift_observation.model_copy(
        update={
            "disposition": ChangeDisposition.MISSING,
            "expected_locator_visible_count": 0,
            "semantic_visible_count": 0,
            "current_locator_strategy": None,
            "current_locator_value": None,
            "observed_attributes": (),
        }
    )
    with pytest.raises(ValueError, match="cannot become observed"):
        observed_element_from_regression(
            observation_inventory.items[0],
            missing,
            evidence_id="ev_missing",
            observed_at=fixed_now,
        )
