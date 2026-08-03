from test_cartographer.execution.assessment import assess_execution_evidence
from test_cartographer.execution.enums import ExecutionIssueCode
from test_cartographer.execution.models import ExecutionEvidenceBundle


def test_reference_bundle_is_ready_for_reactive_maintenance(execution_bundle):
    report = assess_execution_evidence(execution_bundle)
    assert report.failure_count == 2
    assert report.actionable_failure_count == 2
    assert report.ready_for_reactive_maintenance is True
    assert report.issue_codes == ()


def test_incomplete_failure_traceability_blocks_maintenance(execution_bundle):
    payload = execution_bundle.model_dump(mode="json")
    failed = next(item for item in payload["records"] if item["outcome"] == "test_failure")
    failed["traceability"]["context_id"] = None
    failed["traceability"]["complete"] = False
    failed["traceability"]["missing_fields"] = ["context_id"]
    bundle = ExecutionEvidenceBundle.model_validate(payload)
    report = assess_execution_evidence(bundle)
    assert report.ready_for_reactive_maintenance is False
    assert ExecutionIssueCode.INCOMPLETE_TRACEABILITY in report.issue_codes


def test_missing_last_step_blocks_maintenance(execution_bundle):
    payload = execution_bundle.model_dump(mode="json")
    failed = next(item for item in payload["records"] if item["outcome"] == "test_failure")
    failed["steps"] = []
    bundle = ExecutionEvidenceBundle.model_validate(payload)
    report = assess_execution_evidence(bundle)
    assert report.ready_for_reactive_maintenance is False
    assert ExecutionIssueCode.MISSING_LAST_STEP in report.issue_codes


def test_truncated_bundle_is_not_ready_for_automatic_handoff(execution_bundle):
    payload = execution_bundle.model_dump(mode="json")
    payload["truncated_record_count"] = 1
    bundle = ExecutionEvidenceBundle.model_validate(payload)
    report = assess_execution_evidence(bundle)
    assert report.ready_for_reactive_maintenance is False
    assert ExecutionIssueCode.RECORDS_TRUNCATED in report.issue_codes
