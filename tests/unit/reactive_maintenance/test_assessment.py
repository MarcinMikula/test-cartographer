from test_cartographer.execution.enums import ExecutionOutcome, ExecutionPhase
from test_cartographer.reactive_maintenance.assessment import (
    assess_failure_for_maintenance,
    assess_reactive_maintenance_run,
)
from test_cartographer.reactive_maintenance.enums import MaintenanceDisposition


def test_matching_test_failure_is_ready_only_for_reobservation(
    failure_bundle, maintenance_profile
) -> None:
    result = assess_failure_for_maintenance(failure_bundle, maintenance_profile)
    assert result.disposition is MaintenanceDisposition.REOBSERVATION_REQUIRED
    assert result.ready_for_reobservation is True
    assert result.application_bug_claimed is False
    assert result.stale_locator_claimed is False
    assert result.infrastructure_error_excluded is True


def test_infrastructure_error_blocks_repair(failure_bundle, maintenance_profile) -> None:
    record = failure_bundle.records[0]
    infra = record.model_copy(
        update={
            "outcome": ExecutionOutcome.INFRASTRUCTURE_ERROR,
            "failure": record.failure.model_copy(update={"phase": ExecutionPhase.SETUP}),
        }
    )
    bundle = failure_bundle.model_copy(
        update={
            "records": (infra,),
            "test_failure_count": 0,
            "infrastructure_error_count": 1,
        }
    )
    result = assess_failure_for_maintenance(bundle, maintenance_profile)
    assert result.disposition is MaintenanceDisposition.INFRASTRUCTURE_BLOCKED
    assert result.ready_for_reobservation is False


def test_wrong_last_step_is_insufficient(failure_bundle, maintenance_profile) -> None:
    record = failure_bundle.records[0]
    wrong = record.steps[0].model_copy(update={"locator_id": "loc_other_target"})
    bundle = failure_bundle.model_copy(
        update={"records": (record.model_copy(update={"steps": (wrong,)}),)}
    )
    result = assess_failure_for_maintenance(bundle, maintenance_profile)
    assert result.disposition is MaintenanceDisposition.INSUFFICIENT_EVIDENCE
    assert "last_step_does_not_match_maintenance_target" in result.issue_codes
