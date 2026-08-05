from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.execution.enums import (
    ExecutionAction,
    ExecutionOutcome,
    ExecutionPhase,
)
from test_cartographer.execution.models import (
    ExecutionEvidenceBundle,
    ExecutionEvidenceRecord,
    ExecutionStep,
    ExecutionTraceability,
    FailureSummary,
    RuntimeEnvironment,
    TestIdentity,
)
from test_cartographer.reactive_maintenance.io import load_maintenance_profile


@pytest.fixture
def maintenance_profile():
    return load_maintenance_profile(
        "testdata/maintenance/profile/reactive_catalog.json"
    )


@pytest.fixture
def failure_bundle() -> ExecutionEvidenceBundle:
    now = datetime(2026, 8, 5, 18, 0, tzinfo=timezone.utc)
    record = ExecutionEvidenceRecord(
        id="exe_maintenance_failure",
        run_id="run_maintenance_failure",
        profile_id="execution_maintenance_catalog",
        captured_at=now,
        outcome=ExecutionOutcome.TEST_FAILURE,
        test=TestIdentity(
            nodeid="tests/e2e/test_search_catalog.py::test_search_catalog",
            relative_path="tests/e2e/test_search_catalog.py",
            test_name="test_search_catalog",
            line_number=20,
            marker_names=("e2e",),
        ),
        traceability=ExecutionTraceability(
            context_id="ctx_cb1897ffad97",
            process_id="proc_target",
            synthesis_run_id="synrun_210caae45058",
            adaptation_plan_id="adapt_a60379078f5b",
            code_patch_id="patch_rereview_7c2de0c8e20e",
            source_ids=("method_submit_search",),
            complete=True,
            missing_fields=(),
        ),
        environment=RuntimeEnvironment(
            framework_id="qa_automation_framework_reference",
            environment_label="controlled_changed_catalog",
            python_version="3.11.9",
            pytest_version="9.1.1",
            playwright_version="1.62.0",
            platform_system="Windows",
        ),
        duration_seconds=1.2,
        steps=(
            ExecutionStep(
                sequence=1,
                step_id="step_submit_search",
                page_object="CatalogSearchForm",
                method_name="submit_search",
                action=ExecutionAction.CLICK,
                target_element_id="el_search_submit",
                locator_id="loc_el_search_submit_1",
            ),
        ),
        failure=FailureSummary(
            phase=ExecutionPhase.CALL,
            exception_type="TimeoutError",
            safe_summary="TimeoutError during call",
            message_sha256="a" * 64,
            traceback_sha256="b" * 64,
            redaction_count=0,
            message_truncated=False,
        ),
        sensitivity=SensitivityLevel.INTERNAL,
    )
    return ExecutionEvidenceBundle(
        id="bundle_maintenance_failure",
        run_id="run_maintenance_failure",
        profile_id="execution_maintenance_catalog",
        started_at=now,
        completed_at=now + timedelta(seconds=2),
        records=(record,),
        passed_count=0,
        test_failure_count=1,
        infrastructure_error_count=0,
    )

@pytest.fixture
def passed_maintenance_run():
    from test_cartographer.reactive_maintenance.enums import (
        MaintenanceActionKind,
        MaintenanceStatus,
    )
    from test_cartographer.reactive_maintenance.models import (
        MaintenanceActionRecord,
        ReactiveMaintenanceRun,
    )

    now = datetime(2026, 8, 5, 19, 0, tzinfo=timezone.utc)
    actions = tuple(
        MaintenanceActionRecord(
            sequence=index,
            kind=kind,
            target_id=f"maintenance_target_{index}",
            decision="accepted" if kind is not MaintenanceActionKind.CANDIDATE_SELECTION else "cand_002",
            started_at=now + timedelta(seconds=index),
            completed_at=now + timedelta(seconds=index + 1),
            active_seconds=1.0,
        )
        for index, kind in enumerate(MaintenanceActionKind, start=1)
    )
    return ReactiveMaintenanceRun(
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
