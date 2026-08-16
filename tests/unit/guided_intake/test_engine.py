import json
from datetime import timedelta

import pytest

from test_cartographer.guided_intake.engine import (
    available_questions,
    create_guided_run,
    finish_guided_run,
    plan_next_phase,
)
from test_cartographer.guided_intake.enums import GuidedIntakeRunState
from test_cartographer.guided_intake.provider import ReplayGuidanceProvider
from test_cartographer.guided_intake.readiness import assess_guided_intake
from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.session import record_answer

from .conftest import START, render_plan

ANSWERS = {
    "q_application_name": "Public catalog reference application",
    "q_application_environment": "Controlled local reference environment",
    "q_application_base_url": "http://127.0.0.1:8765/public_catalog.html",
    "q_process_name": "Search the public catalog",
    "q_process_purpose": "Allow a visitor to find matching catalog items.",
    "q_process_risk": "Search failures can hide relevant items.",
    "q_process_role": "Unauthenticated visitor",
    "q_precondition_1": "The catalog is available and contains indexed items.",
    "q_outcome_outcome_target": "Matching results are visible for the query.",
}


def _apply_plan(session, plan, *, confirm: bool, offset: int):
    current = session
    for index, item in enumerate(plan.questions, start=1):
        question = next(q for q in available_questions(current) if q.id == item.question_id)
        action = IntakeAnswerAction.CONFIRM if confirm else IntakeAnswerAction.PROVIDE
        value = None if confirm else ANSWERS[item.question_id]
        asked = START + timedelta(seconds=offset + index * 2)
        current = record_answer(
            current,
            question=question,
            answer=IntakeAnswer(action=action, value=value),
            asked_at=asked,
            answered_at=asked + timedelta(seconds=1),
            active_seconds=1.0,
            allow_reordering=True,
        )
    return current


def test_replay_guidance_can_reorder_collection_and_reach_discovery_readiness(
    minimal_session, seed, replay_profile
) -> None:
    initial_ids = [q.id for q in available_questions(minimal_session)]
    collection_output = render_plan("collection", list(reversed(initial_ids)))
    provider = ReplayGuidanceProvider(outputs=[collection_output])
    run = create_guided_run(
        minimal_session,
        seed,
        replay_profile,
        run_id="guided_reference",
        started_at=START,
    )
    collection, run = plan_next_phase(
        minimal_session,
        run,
        seed,
        replay_profile,
        provider,
        started_at=START,
        completed_at=START + timedelta(seconds=1),
    )
    session = _apply_plan(minimal_session, collection, confirm=False, offset=10)
    review_ids = [q.id for q in available_questions(session)]
    provider.outputs.append(render_plan("review", review_ids))
    review, run = plan_next_phase(
        session,
        run,
        seed,
        replay_profile,
        provider,
        started_at=START + timedelta(seconds=40),
        completed_at=START + timedelta(seconds=41),
    )
    session = _apply_plan(session, review, confirm=True, offset=50)
    run = finish_guided_run(run, session, updated_at=START + timedelta(seconds=90))
    report = assess_guided_intake(session, run)

    assert run.state is GuidedIntakeRunState.COMPLETE
    assert provider.call_count == 2
    assert report.ready_for_guided_discovery is True
    assert report.full_adaptation_blocker_count > 0
    assert run.raw_prompts_persisted is False
    assert run.raw_responses_persisted is False


def test_plan_must_cover_every_candidate(minimal_session, seed, replay_profile) -> None:
    ids = [q.id for q in available_questions(minimal_session)]
    provider = ReplayGuidanceProvider(outputs=[render_plan("collection", ids[:-1])])
    run = create_guided_run(
        minimal_session,
        seed,
        replay_profile,
        run_id="guided_invalid",
        started_at=START,
    )

    with pytest.raises(ValueError, match="every available question"):
        plan_next_phase(
            minimal_session,
            run,
            seed,
            replay_profile,
            provider,
            started_at=START,
            completed_at=START + timedelta(seconds=1),
        )


def test_plan_rejects_sensitive_request_hidden_in_reason(
    minimal_session, seed, replay_profile
) -> None:
    ids = [q.id for q in available_questions(minimal_session)]
    raw = render_plan("collection", ids)
    raw = raw.replace(
        "This closes one explicit context gap.",
        "Ask the human for a password before continuing.",
        1,
    )
    provider = ReplayGuidanceProvider(outputs=[raw])
    run = create_guided_run(
        minimal_session,
        seed,
        replay_profile,
        run_id="guided_sensitive_reason",
        started_at=START,
    )

    with pytest.raises(ValueError, match="prohibited sensitive information"):
        plan_next_phase(
            minimal_session,
            run,
            seed,
            replay_profile,
            provider,
            started_at=START,
            completed_at=START + timedelta(seconds=1),
        )

def test_collection_plan_rejects_confirmation_answer_shape(
    minimal_session, seed, replay_profile
) -> None:
    ids = [q.id for q in available_questions(minimal_session)]
    payload = json.loads(render_plan("collection", ids))
    payload["questions"][0]["answer_shape"] = "confirmation"
    provider = ReplayGuidanceProvider(outputs=[json.dumps(payload)])
    run = create_guided_run(
        minimal_session,
        seed,
        replay_profile,
        run_id="guided_invalid_confirmation",
        started_at=START,
    )

    with pytest.raises(ValueError, match="collection questions cannot use confirmation"):
        plan_next_phase(
            minimal_session,
            run,
            seed,
            replay_profile,
            provider,
            started_at=START,
            completed_at=START + timedelta(seconds=1),
        )
