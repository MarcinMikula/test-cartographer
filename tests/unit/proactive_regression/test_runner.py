from test_cartographer.proactive_regression.enums import (
    AutomationImpact,
    ChangeDisposition,
)
from test_cartographer.proactive_regression.runner import (
    _format_inventory,
    format_frontend_change_report,
)


def test_reference_run_preserves_green_test_and_detected_drift(passed_run) -> None:
    assert passed_run.baseline_probe.passed is True
    assert passed_run.current_probe.passed is True
    assert passed_run.report.locator_drift_count == 1
    assert (
        passed_run.framework_source_fingerprint_before
        == passed_run.framework_source_fingerprint_after
    )


def test_uncovered_drift_is_mapped_context_staleness(passed_run) -> None:
    drift = next(
        item for item in passed_run.report.observations
        if item.disposition is ChangeDisposition.LOCATOR_DRIFT
    )
    assert drift.covered_by_current_framework_test is False
    assert drift.automation_impact is AutomationImpact.MAPPED_CONTEXT_STALE


def test_report_formatter_discloses_review_only_boundary(passed_run, inventory) -> None:
    inventory_text = _format_inventory(inventory)
    assert "navigation_timeout_ms=30000" in inventory_text
    assert "locator_timeout_ms=2000" in inventory_text

    text = format_frontend_change_report(passed_run.report)
    assert "Application bug claimed: false" in text
    assert "Automatic patch created: false" in text
    assert "Live LLM used: false" in text
