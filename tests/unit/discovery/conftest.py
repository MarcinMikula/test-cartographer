from __future__ import annotations

from datetime import datetime, timezone

import pytest

from test_cartographer.context.enums import ActionKind, LocatorStrategy
from test_cartographer.discovery.enums import DiscoveryProviderKind
from test_cartographer.discovery.models import (
    CandidateAttribute,
    DiscoveredLocator,
    DiscoveryProfile,
    DiscoveryTarget,
    ElementCandidate,
    ProcessDiscoveryPlan,
)


@pytest.fixture
def profile() -> DiscoveryProfile:
    return DiscoveryProfile(
        id="discovery_test",
        provider=DiscoveryProviderKind.REPLAY,
        model="replay-discovery",
        base_url="replay://local",
        timeout_seconds=10.0,
        max_elements_scanned=40,
        max_candidates_per_target=4,
        minimum_candidate_score=45,
        ambiguity_score_delta=3,
    )


def _locator(identifier, strategy, value, priority=10, count=1):
    return DiscoveredLocator(
        id=identifier,
        strategy=strategy,
        value=value,
        match_count=count,
        priority=priority,
    )


@pytest.fixture
def candidates() -> tuple[ElementCandidate, ...]:
    return (
        ElementCandidate(
            id="cand_001",
            ordinal=1,
            tag_name="input",
            semantic_role="searchbox",
            semantic_name="Search catalog",
            enabled=True,
            editable=True,
            attributes=(
                CandidateAttribute(name="id", value="catalog-query"),
                CandidateAttribute(name="label", value="Search catalog"),
            ),
            locator_candidates=(
                _locator("dc_001_01", LocatorStrategy.LABEL, "Search catalog"),
            ),
        ),
        ElementCandidate(
            id="cand_002",
            ordinal=2,
            tag_name="button",
            semantic_role="button",
            semantic_name="Search",
            enabled=True,
            editable=False,
            attributes=(CandidateAttribute(name="data-testid", value="search-submit"),),
            locator_candidates=(
                _locator("dc_002_01", LocatorStrategy.TEST_ID, "search-submit"),
                _locator("dc_002_02", LocatorStrategy.ROLE, "button:Search", 30, 2),
            ),
        ),
        ElementCandidate(
            id="cand_003",
            ordinal=3,
            tag_name="button",
            semantic_role="button",
            semantic_name="Search",
            enabled=True,
            editable=False,
            attributes=(CandidateAttribute(name="data-testid", value="search-help"),),
            locator_candidates=(
                _locator("dc_003_01", LocatorStrategy.TEST_ID, "search-help"),
                _locator("dc_003_02", LocatorStrategy.ROLE, "button:Search", 30, 2),
            ),
        ),
        ElementCandidate(
            id="cand_004",
            ordinal=4,
            tag_name="ul",
            semantic_role="list",
            semantic_name="Catalog results",
            enabled=True,
            editable=False,
            attributes=(CandidateAttribute(name="data-testid", value="catalog-results"),),
            locator_candidates=(
                _locator("dc_004_01", LocatorStrategy.TEST_ID, "catalog-results"),
            ),
        ),
    )


@pytest.fixture
def plan() -> ProcessDiscoveryPlan:
    return ProcessDiscoveryPlan(
        id="discovery_plan_public_catalog",
        context_id="ctx_product_search_minimal",
        process_id="proc_target",
        page_id="page_catalog",
        page_name="Public catalog",
        route="/public_catalog_discovery.html",
        source_url="http://127.0.0.1:8765/public_catalog_discovery.html",
        component_ids=("comp_catalog_search",),
        targets=(
            DiscoveryTarget(
                id="target_search_query",
                element_id="el_search_query",
                owner_id="comp_catalog_search",
                name="Search catalog query",
                action_kind=ActionKind.FILL,
                expected_roles=("searchbox", "textbox"),
                test_data_symbolic_ref="catalog_query",
            ),
            DiscoveryTarget(
                id="target_search_submit",
                element_id="el_search_submit",
                owner_id="comp_catalog_search",
                name="Search action",
                action_kind=ActionKind.CLICK,
                expected_roles=("button",),
            ),
            DiscoveryTarget(
                id="target_search_results",
                element_id="el_search_results",
                owner_id="page_catalog",
                name="Catalog results",
                action_kind=ActionKind.READ,
                expected_roles=("list",),
                outcome_target=True,
            ),
        ),
    )
