"""Replay the complete minimal-seed guided-intake flow deterministically."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.io import save_context
from test_cartographer.guided_intake.engine import (
    available_questions,
    create_guided_run,
    finish_guided_run,
    plan_next_phase,
)
from test_cartographer.guided_intake.io import (
    load_guided_profile,
    load_minimal_seed,
    save_guided_run,
)
from test_cartographer.guided_intake.provider import ReplayGuidanceProvider
from test_cartographer.guided_intake.readiness import assess_guided_intake
from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.io import save_session
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.seed import build_minimal_context
from test_cartographer.intake.session import create_session, record_answer

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)
ANSWERS = {
    "q_application_name": "Public catalog reference application",
    "q_application_environment": "Controlled local reference environment",
    "q_application_base_url": "http://127.0.0.1:8765/public_catalog.html",
    "q_process_name": "Search the public catalog",
    "q_process_purpose": "Allow a visitor to find matching catalog items.",
    "q_process_risk": "Search failures can hide relevant items.",
    "q_process_role": "Unauthenticated visitor",
    "q_precondition_1": "The catalog is available and contains indexed items.",
    "q_outcome_outcome_target": "Matching product results are visible for the supplied query.",
}


def _render(phase: str, ids: list[str]) -> str:
    return json.dumps(
        {
            "schema_version": "0.1",
            "phase": phase,
            "questions": [
                {
                    "question_id": question_id,
                    "user_prompt": f"Please answer {question_id}.",
                    "reason": "This closes one explicit context gap.",
                    "answer_shape": (
                        "confirmation" if phase == "review" else "sentence"
                    ),
                }
                for question_id in ids
            ],
        }
    )


def _apply(session, plan, *, confirm: bool, offset: int):
    current = session
    for index, item in enumerate(plan.questions, start=1):
        question = next(q for q in available_questions(current) if q.id == item.question_id)
        asked = START + timedelta(seconds=offset + index * 2)
        current = record_answer(
            current,
            question=question,
            answer=IntakeAnswer(
                action=(
                    IntakeAnswerAction.CONFIRM
                    if confirm
                    else IntakeAnswerAction.PROVIDE
                ),
                value=None if confirm else ANSWERS[item.question_id],
            ),
            asked_at=asked,
            answered_at=asked + timedelta(seconds=1),
            active_seconds=1.0,
            allow_reordering=True,
        )
    return current


def main() -> None:
    seed = load_minimal_seed(
        ROOT / "testdata/guided_intake/seed/product_search.json"
    )
    profile = load_guided_profile(
        ROOT / "testdata/guided_intake/profile/replay.json"
    )
    session = create_session(
        build_minimal_context(seed),
        session_id="intake_guided_replay",
        started_at=START,
    )
    run = create_guided_run(
        session,
        seed,
        profile,
        run_id="guided_replay_reference",
        started_at=START,
    )
    collection_ids = [q.id for q in available_questions(session)]
    provider = ReplayGuidanceProvider(
        outputs=[_render("collection", list(reversed(collection_ids)))]
    )
    collection, run = plan_next_phase(
        session,
        run,
        seed,
        profile,
        provider,
        started_at=START,
        completed_at=START + timedelta(seconds=1),
    )
    session = _apply(session, collection, confirm=False, offset=10)
    review_ids = [q.id for q in available_questions(session)]
    provider.outputs.append(_render("review", review_ids))
    review, run = plan_next_phase(
        session,
        run,
        seed,
        profile,
        provider,
        started_at=START + timedelta(seconds=40),
        completed_at=START + timedelta(seconds=41),
    )
    session = _apply(session, review, confirm=True, offset=50)
    run = finish_guided_run(run, session, updated_at=START + timedelta(seconds=90))
    report = assess_guided_intake(session, run)
    if not report.ready_for_guided_discovery:
        raise RuntimeError("replay guided intake did not reach discovery readiness")
    if report.full_adaptation_blocker_count == 0:
        raise RuntimeError("Sprint 8 must not pretend technical discovery is complete")

    target = ROOT / ".test-cartographer/sprint-8/replay"
    target.mkdir(parents=True, exist_ok=True)
    save_context(session.context, target / "context.json")
    save_session(session, target / "session.json")
    save_guided_run(run, target / "run.json")

    print("Minimal human request expanded into nine explicit intake questions.")
    print("Replay LLM guidance reordered collection without inventing question IDs.")
    print("Human answers remained authoritative and were confirmed separately.")
    print("Human intake reached readiness for guided process discovery.")
    print("Full adaptation remained blocked until browser discovery supplies technical evidence.")
    print("Raw prompts and raw model responses were not persisted.")
    print("Live provider used: false")


if __name__ == "__main__":
    main()
