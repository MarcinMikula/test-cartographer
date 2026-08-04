from datetime import datetime, timedelta, timezone

import pytest

from test_cartographer.creation_flow.enums import (
    CreationFlowStatus,
    CreationStageKind,
    CreationStageStatus,
)
from test_cartographer.creation_flow.models import CreationFlowRun, CreationStageRecord


@pytest.fixture
def passed_creation_run() -> CreationFlowRun:
    started = datetime(2026, 8, 4, 16, 0, tzinfo=timezone.utc)
    stages = tuple(
        CreationStageRecord(
            kind=kind,
            status=CreationStageStatus.PASSED,
            started_at=started + timedelta(seconds=index),
            completed_at=started + timedelta(seconds=index + 1),
            duration_seconds=1.0,
            live_llm_calls=2 if kind is CreationStageKind.GUIDED_INTAKE else (1 if kind is CreationStageKind.BROWSER_DISCOVERY else 0),
            deterministic_operations=1,
            browser_operations=1 if kind in {CreationStageKind.BROWSER_DISCOVERY, CreationStageKind.FRAMEWORK_EXECUTION} else 0,
            human_actions=1,
            artifact_ids=(f"artifact_{index}",),
            summary=f"Completed {kind.value}.",
        )
        for index, kind in enumerate(CreationStageKind)
    )
    return CreationFlowRun(
        id="creation_flow_test",
        profile_id="creation_profile_test",
        context_id="ctx_creation_test",
        status=CreationFlowStatus.PASSED,
        started_at=started,
        completed_at=started + timedelta(seconds=20),
        target_test="tests/e2e/test_search_catalog.py",
        stages=stages,
        total_seconds=20.0,
        model_seconds=3.0,
        browser_seconds=2.0,
        verification_seconds=1.0,
        human_active_seconds=5.0,
        live_llm_call_count=3,
        deterministic_synthesis_call_count=1,
        human_answer_count=9,
        human_confirmation_count=5,
        handoff_confirmation_count=4,
        ambiguity_resolution_count=1,
        review_decision_count=4,
        total_human_action_count=23,
        candidate_count=4,
        target_count=3,
        generated_file_count=3,
        modified_file_count=1,
        reused_symbol_count=0,
        collected_test_count=1,
        passed_test_count=1,
        live_llm_used=True,
        framework_execution_independent=True,
        original_framework_unchanged=True,
        full_traceability=True,
    )
