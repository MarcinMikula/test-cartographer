"""Deterministic assessment for the Sprint 13 proof boundary."""

from test_cartographer.proactive_regression.enums import (
    ProactiveRunStatus,
    ReportReviewDecision,
)
from test_cartographer.proactive_regression.models import (
    ProactiveRegressionAssessment,
    ProactiveRegressionRun,
)


def assess_proactive_regression_run(
    run: ProactiveRegressionRun,
) -> ProactiveRegressionAssessment:
    blockers: list[str] = []
    if run.status is not ProactiveRunStatus.PASSED:
        blockers.append("run did not finish in passed state")
    if not run.baseline_probe.passed:
        blockers.append("framework probe was not green on the baseline page")
    if not run.current_probe.passed:
        blockers.append("framework probe was not green on the current page")
    if run.report.stable_count < 1:
        blockers.append("no approved mapped element remained stable")
    if run.report.locator_drift_count < 1:
        blockers.append("no approved mapped locator drift was detected")
    if run.report.mapped_context_stale_count < 1:
        blockers.append("detected drift was not classified as mapped-context staleness")
    if run.report.decision is not ReportReviewDecision.ACCEPTED:
        blockers.append("change-impact report was not accepted by the operator")
    if run.operator_action_count != 3:
        blockers.append("real flow did not preserve exactly three bounded operator actions")
    if not run.accepted_inventory_reused:
        blockers.append("accepted observation inventory was not reused")
    if run.interactive_human_trigger_used and not run.headed_browser_used:
        blockers.append("real operator flow did not use headed browser observation")
    if run.application_bug_claimed:
        blockers.append("run made an unsupported application-bug claim")
    if run.automatic_patch_created or run.context_automatically_modified:
        blockers.append("run crossed the review-only Sprint 13 boundary")
    if run.live_llm_used or run.raw_page_persisted:
        blockers.append("run crossed the provider or privacy boundary")

    verified = not blockers
    controlled_demo_ready = verified and run.interactive_human_trigger_used
    return ProactiveRegressionAssessment(
        run_id=run.id,
        blockers=tuple(blockers),
        proactive_regression_verified=verified,
        controlled_demo_ready=controlled_demo_ready,
    )
