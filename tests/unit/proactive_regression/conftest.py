import json
from pathlib import Path

import pytest

from test_cartographer.proactive_regression.models import (
    ObservationInventory,
    ProactiveRegressionProfile,
)

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def inventory() -> ObservationInventory:
    return ObservationInventory.model_validate_json(
        (ROOT / "testdata/proactive/inventory/public_catalog.json").read_text(encoding="utf-8")
    )


@pytest.fixture
def profile() -> ProactiveRegressionProfile:
    return ProactiveRegressionProfile.model_validate_json(
        (ROOT / "testdata/proactive/profile/bounded_public.json").read_text(encoding="utf-8")
    )
@pytest.fixture
def passed_run():
    from datetime import datetime, timezone
    from test_cartographer.context.enums import LocatorStrategy
    from test_cartographer.proactive_regression.enums import (
        AutomationImpact, ChangeDisposition, ProactiveRunStatus, ReportReviewDecision
    )
    from test_cartographer.proactive_regression.models import (
        ElementRegressionObservation, FrameworkProbeResult, FrontendChangeReport,
        ProactiveRegressionRun
    )
    now = datetime(2026, 8, 6, 17, 0, tzinfo=timezone.utc)
    observations = (
        ElementRegressionObservation(
            item_id="inventory_search_submit", element_id="el_search_submit",
            disposition=ChangeDisposition.UNCHANGED,
            automation_impact=AutomationImpact.NONE_DETECTED,
            covered_by_current_framework_test=True,
            expected_locator_strategy=LocatorStrategy.TEST_ID,
            expected_locator_value="search-submit",
            expected_locator_visible_count=1, semantic_visible_count=1,
            current_locator_strategy=LocatorStrategy.TEST_ID,
            current_locator_value="search-submit",
            observed_attributes=(), observation_sha256="a" * 64,
        ),
        ElementRegressionObservation(
            item_id="inventory_sort_results", element_id="el_sort_results",
            disposition=ChangeDisposition.LOCATOR_DRIFT,
            automation_impact=AutomationImpact.MAPPED_CONTEXT_STALE,
            covered_by_current_framework_test=False,
            expected_locator_strategy=LocatorStrategy.TEST_ID,
            expected_locator_value="catalog-sort",
            expected_locator_visible_count=0, semantic_visible_count=1,
            current_locator_strategy=LocatorStrategy.TEST_ID,
            current_locator_value="catalog-sort-control",
            observed_attributes=(), observation_sha256="b" * 64,
        ),
    )
    report = FrontendChangeReport(
        id="report_reference_proactive", run_id="proactive_reference_run",
        inventory_id="inventory_public_catalog", generated_at=now,
        decision=ReportReviewDecision.ACCEPTED, observations=observations,
        stable_count=1, locator_drift_count=1, missing_count=0,
        ambiguous_count=0, current_test_risk_count=0,
        mapped_context_stale_count=1,
    )
    probe_before = FrameworkProbeResult(
        phase="baseline", collected_test_count=1, passed_test_count=1,
        failed_test_count=0, infrastructure_error_count=0, passed=True,
    )
    probe_after = probe_before.model_copy(update={"phase": "current"})
    return ProactiveRegressionRun(
        id="proactive_reference_run", profile_id="proactive_profile_public",
        inventory_id="inventory_public_catalog", started_at=now, finished_at=now,
        status=ProactiveRunStatus.PASSED, operator_action_count=3,
        interactive_human_trigger_used=True, fixture_decisions_used=False,
        headed_browser_used=True, accepted_inventory_reused=True,
        baseline_probe=probe_before, current_probe=probe_after, report=report,
        framework_source_fingerprint_before="c" * 64,
        framework_source_fingerprint_after="c" * 64,
    )
