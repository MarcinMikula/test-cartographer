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


@pytest.fixture
def passed_creation_run():
    from datetime import datetime, timedelta, timezone

    from test_cartographer.creation_flow.enums import (
        CreationFlowStatus,
        CreationStageKind,
        CreationStageStatus,
    )
    from test_cartographer.creation_flow.models import CreationFlowRun, CreationStageRecord

    started = datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc)
    stages = tuple(
        CreationStageRecord(
            kind=kind,
            status=CreationStageStatus.PASSED,
            started_at=started + timedelta(seconds=index),
            completed_at=started + timedelta(seconds=index + 1),
            duration_seconds=1.0,
            live_llm_calls=(2 if kind is CreationStageKind.GUIDED_INTAKE else 1 if kind is CreationStageKind.BROWSER_DISCOVERY else 0),
            deterministic_operations=1,
            browser_operations=1 if kind in {CreationStageKind.BROWSER_DISCOVERY, CreationStageKind.FRAMEWORK_EXECUTION} else 0,
            human_actions=1,
            artifact_ids=(f"artifact_{index}",),
            summary=f"Completed {kind.value}.",
        )
        for index, kind in enumerate(CreationStageKind)
    )
    return CreationFlowRun(
        id="creation_flow_test",
        profile_id="creation_profile_test",
        context_id="ctx_creation_test",
        status=CreationFlowStatus.PASSED,
        started_at=started,
        completed_at=started + timedelta(seconds=20),
        target_test="tests/e2e/test_search_catalog.py",
        stages=stages,
        total_seconds=20.0,
        model_seconds=3.0,
        browser_seconds=2.0,
        verification_seconds=1.0,
        human_active_seconds=5.0,
        live_llm_call_count=3,
        deterministic_synthesis_call_count=1,
        human_answer_count=9,
        human_confirmation_count=5,
        handoff_confirmation_count=4,
        ambiguity_resolution_count=1,
        review_decision_count=4,
        total_human_action_count=23,
        candidate_count=4,
        target_count=3,
        generated_file_count=3,
        modified_file_count=1,
        reused_symbol_count=0,
        collected_test_count=1,
        passed_test_count=1,
        live_llm_used=True,
        framework_execution_independent=True,
        original_framework_unchanged=True,
        full_traceability=True,
    )
