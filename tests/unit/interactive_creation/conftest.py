from datetime import datetime, timedelta, timezone

import pytest

from test_cartographer.creation_flow.models import CreationFlowRun
from test_cartographer.interactive_creation.enums import (
    InteractiveSessionState,
    OperatorActionKind,
)
from test_cartographer.interactive_creation.models import (
    InteractiveCreationProfile,
    InteractiveOperatorSession,
    OperatorActionRecord,
)


@pytest.fixture
def interactive_profile() -> InteractiveCreationProfile:
    return InteractiveCreationProfile(
        id="interactive_profile_test",
        label="Interactive profile test",
        target_test="tests/e2e/test_search_catalog.py",
        minimum_intake_answers=9,
        minimum_intake_confirmations=1,
        minimum_review_decisions=4,
    )


@pytest.fixture
def interactive_creation_run(passed_creation_run) -> CreationFlowRun:
    payload = passed_creation_run.model_dump(mode="python")
    payload.update(
        {
            "id": "creation_flow_interactive_test",
            "profile_id": "interactive_profile_test",
            "fixture_assisted_reference_demo": False,
            "interactive_human_used_during_verifier": True,
            "live_llm_call_count": 2,
            "human_trigger_count": 1,
            "human_answer_count": 9,
            "human_confirmation_count": 1,
            "handoff_confirmation_count": 1,
            "ambiguity_resolution_count": 1,
            "review_decision_count": 4,
            "execution_trigger_count": 1,
            "total_human_action_count": 18,
        }
    )
    return CreationFlowRun.model_validate(payload)


@pytest.fixture
def operator_session(interactive_creation_run) -> InteractiveOperatorSession:
    started = datetime(2026, 8, 4, 18, 0, tzinfo=timezone.utc)
    specs: list[tuple[OperatorActionKind, str, str]] = [
        (OperatorActionKind.INITIAL_REQUEST, "minimal_request", "provided"),
    ]
    specs.extend(
        (OperatorActionKind.INTAKE_ANSWER, f"q_answer_{index}", "provide")
        for index in range(1, 10)
    )
    specs.append(
        (
            OperatorActionKind.INTAKE_CONFIRMATION,
            "process_context_summary",
            "confirmed_all",
        )
    )
    specs.append(
        (
            OperatorActionKind.SYNTHESIS_HANDOFF_CONFIRMATION,
            "synthesis_handoff",
            "accepted",
        )
    )
    specs.append(
        (OperatorActionKind.AMBIGUITY_SELECTION, "amb_search", "cand_002")
    )
    specs.extend(
        (OperatorActionKind.REVIEW_DECISION, target, "accepted")
        for target in ("discovery", "pom", "plan", "patch")
    )
    specs.append(
        (OperatorActionKind.EXECUTION_TRIGGER, "execution", "accepted")
    )
    actions = tuple(
        OperatorActionRecord(
            sequence=index,
            kind=kind,
            target_id=target,
            decision=decision,
            started_at=started + timedelta(seconds=index),
            completed_at=started + timedelta(seconds=index + 1),
            active_seconds=1.0,
        )
        for index, (kind, target, decision) in enumerate(specs, start=1)
    )
    return InteractiveOperatorSession(
        id="operator_session_test",
        profile_id="interactive_profile_test",
        state=InteractiveSessionState.COMPLETE,
        started_at=started,
        updated_at=started + timedelta(seconds=60),
        creation_flow_run_id=interactive_creation_run.id,
        actions=actions,
        headed_browser_used=True,
    )
