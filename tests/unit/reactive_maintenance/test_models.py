from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.context.enums import LocatorStrategy
from test_cartographer.reactive_maintenance.enums import (
    MaintenanceActionKind,
    MaintenanceDecision,
    MaintenanceStatus,
)
from test_cartographer.reactive_maintenance.models import (
    MaintenanceActionRecord,
    MaintenanceCandidate,
    MaintenanceSourcePatch,
    ReactiveMaintenanceRun,
)


def test_patch_rejects_hash_mismatch() -> None:
    now = datetime(2026, 8, 5, 18, 0, tzinfo=timezone.utc)
    with pytest.raises(ValidationError, match="hashes"):
        MaintenanceSourcePatch(
            id="maintenance_patch_test",
            diagnosis_id="diagnosis_test",
            profile_id="maintenance_catalog_search",
            created_at=now,
            target_path="components/catalog_search_form.py",
            symbol_name="search_submit",
            expected_before_sha256="a" * 64,
            old_locator_value="search-submit",
            new_locator_value="catalog-search-submit",
            full_source="print('ok')\n",
            full_source_sha256="b" * 64,
            expected_after_sha256="b" * 64,
        )


def test_passed_run_requires_every_operator_boundary() -> None:
    now = datetime(2026, 8, 5, 18, 0, tzinfo=timezone.utc)
    kinds = tuple(MaintenanceActionKind)
    actions = tuple(
        MaintenanceActionRecord(
            sequence=index,
            kind=kind,
            target_id=f"target_{index}",
            decision="accepted",
            started_at=now + timedelta(seconds=index),
            completed_at=now + timedelta(seconds=index + 1),
            active_seconds=1.0,
        )
        for index, kind in enumerate(kinds, start=1)
    )
    run = ReactiveMaintenanceRun(
        id="maintenance_run_test",
        profile_id="maintenance_catalog_search",
        status=MaintenanceStatus.PASSED,
        started_at=now,
        completed_at=now + timedelta(seconds=20),
        source_execution_bundle_id="bundle_failure",
        source_failure_record_id="exe_failure",
        diagnosis_id="diagnosis_test",
        patch_id="maintenance_patch_test",
        before_execution_bundle_id="bundle_failure",
        after_execution_bundle_id="bundle_pass",
        actions=actions,
        candidate_count=2,
        selected_candidate_id="cand_002",
        failed_test_count_before=1,
        infrastructure_error_count_before=0,
        collected_test_count_after=1,
        passed_test_count_after=1,
    )
    assert run.operator_action_count == 5
    assert run.active_seconds == 5.0
