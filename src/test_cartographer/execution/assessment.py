"""Deterministic readiness assessment for future reactive maintenance."""

from __future__ import annotations

from test_cartographer.execution.enums import ExecutionIssueCode, ExecutionOutcome
from test_cartographer.execution.models import (
    ExecutionEvidenceAssessment,
    ExecutionEvidenceBundle,
)


def assess_execution_evidence(
    bundle: ExecutionEvidenceBundle,
) -> ExecutionEvidenceAssessment:
    failures = [record for record in bundle.records if record.outcome is not ExecutionOutcome.PASSED]
    complete = sum(record.traceability.complete for record in bundle.records)
    missing_traceability = sum(not record.traceability.complete for record in failures)
    missing_step = sum(not record.steps for record in failures)
    actionable = sum(
        record.traceability.complete and bool(record.steps) and record.failure is not None
        for record in failures
    )

    issues: list[ExecutionIssueCode] = []
    if not failures:
        issues.append(ExecutionIssueCode.NO_FAILURE_EVIDENCE)
    if missing_traceability:
        issues.append(ExecutionIssueCode.INCOMPLETE_TRACEABILITY)
    if missing_step:
        issues.append(ExecutionIssueCode.MISSING_LAST_STEP)
    if bundle.truncated_record_count:
        issues.append(ExecutionIssueCode.RECORDS_TRUNCATED)

    ready = bool(failures) and actionable == len(failures) and not bundle.truncated_record_count
    return ExecutionEvidenceAssessment(
        bundle_id=bundle.id,
        record_count=len(bundle.records),
        failure_count=len(failures),
        complete_traceability_count=complete,
        actionable_failure_count=actionable,
        missing_traceability_count=missing_traceability,
        missing_last_step_count=missing_step,
        issue_codes=tuple(issues),
        ready_for_reactive_maintenance=ready,
    )
