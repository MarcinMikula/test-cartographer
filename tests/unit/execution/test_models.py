from copy import deepcopy

import pytest
from pydantic import ValidationError

from test_cartographer.execution.models import (
    ExecutionEvidenceBundle,
    ExecutionEvidenceProfile,
    ExecutionEvidenceRecord,
)


def test_reference_profile_is_non_secret_and_bounded(execution_profile):
    assert execution_profile.max_records == 20
    assert execution_profile.max_steps_per_test == 8
    assert execution_profile.credentials_persisted is False
    assert execution_profile.raw_tracebacks_persisted is False
    assert execution_profile.live_llm_used is False


def test_reference_bundle_distinguishes_three_execution_outcomes(execution_bundle):
    assert execution_bundle.passed_count == 1
    assert execution_bundle.test_failure_count == 1
    assert execution_bundle.infrastructure_error_count == 1
    assert {item.outcome.value for item in execution_bundle.records} == {
        "passed",
        "test_failure",
        "infrastructure_error",
    }


def test_passed_record_cannot_contain_failure_details(execution_bundle):
    record = next(item for item in execution_bundle.records if item.outcome.value == "passed")
    payload = record.model_dump(mode="json")
    payload["failure"] = next(
        item.failure.model_dump(mode="json")
        for item in execution_bundle.records
        if item.failure is not None
    )
    with pytest.raises(ValidationError, match="passed execution evidence"):
        ExecutionEvidenceRecord.model_validate(payload)


def test_test_failure_must_originate_in_call_phase(execution_bundle):
    record = next(
        item for item in execution_bundle.records if item.outcome.value == "test_failure"
    )
    payload = record.model_dump(mode="json")
    payload["failure"]["phase"] = "setup"
    with pytest.raises(ValidationError, match="call phase"):
        ExecutionEvidenceRecord.model_validate(payload)


def test_traceability_completeness_cannot_be_claimed_when_field_is_missing(
    execution_bundle,
):
    record = execution_bundle.records[0]
    payload = record.model_dump(mode="json")
    payload["traceability"]["context_id"] = None
    with pytest.raises(ValidationError, match="missing_fields"):
        ExecutionEvidenceRecord.model_validate(payload)


def test_bundle_counts_are_derived_contract_not_free_text(execution_bundle):
    payload = execution_bundle.model_dump(mode="json")
    payload["passed_count"] = 2
    with pytest.raises(ValidationError, match="passed_count"):
        ExecutionEvidenceBundle.model_validate(payload)


def test_privacy_flags_cannot_be_switched_to_true(execution_bundle):
    payload = execution_bundle.records[0].model_dump(mode="json")
    payload["input_values_persisted"] = True
    with pytest.raises(ValidationError):
        ExecutionEvidenceRecord.model_validate(payload)


def test_profile_rejects_duplicate_secret_environment_variable_names(
    execution_profile,
):
    payload = execution_profile.model_dump(mode="json")
    payload["secret_environment_variable_names"] = ["APP_TOKEN", "APP_TOKEN"]
    with pytest.raises(ValidationError, match="must be unique"):
        ExecutionEvidenceProfile.model_validate(payload)


def test_empty_bundle_is_valid_when_passed_records_are_not_collected(execution_bundle):
    payload = execution_bundle.model_dump(mode="json")
    payload.update(
        records=[],
        passed_count=0,
        test_failure_count=0,
        infrastructure_error_count=0,
    )
    empty = ExecutionEvidenceBundle.model_validate(payload)
    assert empty.records == ()
