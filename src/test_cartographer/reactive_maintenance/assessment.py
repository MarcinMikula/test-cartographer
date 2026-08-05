"""Deterministic evidence and completed-run assessment for reactive maintenance."""

from __future__ import annotations

from test_cartographer.execution.enums import ExecutionOutcome
from test_cartographer.execution.models import ExecutionEvidenceBundle
from test_cartographer.reactive_maintenance.enums import (
    MaintenanceDisposition,
    MaintenanceStatus,
)
from test_cartographer.reactive_maintenance.models import (
    MaintenanceEvidenceAssessment,
    ReactiveMaintenanceAssessment,
    ReactiveMaintenanceProfile,
    ReactiveMaintenanceRun,
)


def assess_failure_for_maintenance(
    bundle: ExecutionEvidenceBundle,
    profile: ReactiveMaintenanceProfile,
) -> MaintenanceEvidenceAssessment:
    target_records = [
        record for record in bundle.records if record.test.relative_path == profile.target_test
    ]
    infrastructure = [
        record for record in target_records if record.outcome is ExecutionOutcome.INFRASTRUCTURE_ERROR
    ]
    failures = [
        record for record in target_records if record.outcome is ExecutionOutcome.TEST_FAILURE
    ]
    issues: list[str] = []
    if infrastructure:
        issues.append("target_infrastructure_error")
        return MaintenanceEvidenceAssessment(
            bundle_id=bundle.id,
            record_id=infrastructure[0].id,
            disposition=MaintenanceDisposition.INFRASTRUCTURE_BLOCKED,
            issue_codes=tuple(issues),
        )
    if len(failures) != 1:
        issues.append("exactly_one_target_test_failure_required")
        return MaintenanceEvidenceAssessment(
            bundle_id=bundle.id,
            disposition=MaintenanceDisposition.INSUFFICIENT_EVIDENCE,
            issue_codes=tuple(issues),
        )

    record = failures[0]
    traceability_ok = record.traceability.complete
    if profile.require_complete_traceability and not traceability_ok:
        issues.append("incomplete_traceability")
    last = record.steps[-1] if record.steps else None
    step_ok = bool(
        last
        and last.action == profile.expected_action
        and last.target_element_id == profile.target_element_id
        and last.locator_id == profile.target_locator_id
    )
    if not step_ok:
        issues.append("last_step_does_not_match_maintenance_target")
    ready = traceability_ok and step_ok and record.failure is not None
    if not ready:
        return MaintenanceEvidenceAssessment(
            bundle_id=bundle.id,
            record_id=record.id,
            disposition=MaintenanceDisposition.INSUFFICIENT_EVIDENCE,
            issue_codes=tuple(issues),
            complete_traceability=traceability_ok,
            matching_last_step=step_ok,
        )
    return MaintenanceEvidenceAssessment(
        bundle_id=bundle.id,
        record_id=record.id,
        disposition=MaintenanceDisposition.REOBSERVATION_REQUIRED,
        issue_codes=(),
        infrastructure_error_excluded=True,
        complete_traceability=True,
        matching_last_step=True,
        ready_for_reobservation=True,
    )


def assess_reactive_maintenance_run(
    run: ReactiveMaintenanceRun,
) -> ReactiveMaintenanceAssessment:
    blockers: list[str] = []
    if run.status is not MaintenanceStatus.PASSED:
        blockers.append("maintenance_run_not_passed")
    if not run.human_trigger_used:
        blockers.append("human_trigger_missing")
    if run.fixture_decisions_used:
        blockers.append("fixture_decisions_used")
    if not run.headed_browser_used:
        blockers.append("headed_browser_not_used")
    if not run.exact_patch_reviewed:
        blockers.append("exact_patch_not_reviewed")
    if not run.original_framework_unchanged:
        blockers.append("original_framework_changed")
    if not run.sandbox_only_application:
        blockers.append("patch_not_sandbox_bounded")
    if run.infrastructure_error_count_before:
        blockers.append("infrastructure_error_not_excluded")
    if run.failed_test_count_before < 1:
        blockers.append("pre_repair_failure_not_proven")
    if run.passed_test_count_after < 1:
        blockers.append("post_repair_pass_not_proven")
    if run.live_llm_used:
        blockers.append("unexpected_live_llm_used")
    if run.application_bug_claimed:
        blockers.append("application_bug_claimed_without_basis")
    verified = not blockers
    return ReactiveMaintenanceAssessment(
        run_id=run.id,
        reactive_maintenance_verified=verified,
        controlled_demo_ready=verified,
        blockers=tuple(blockers),
    )
