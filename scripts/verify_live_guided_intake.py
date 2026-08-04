"""Verify two real local-Ollama guided-intake planning rounds."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.context.io import save_context
from test_cartographer.guided_intake.engine import (
    available_questions,
    create_guided_run,
    finish_guided_run,
    plan_next_phase,
)
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.io import load_minimal_seed, save_guided_run
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.guided_intake.provider import OllamaGuidanceProvider
from test_cartographer.guided_intake.readiness import assess_guided_intake
from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.io import save_session
from test_cartographer.intake.models import IntakeAnswer
from test_cartographer.intake.seed import build_minimal_context
from test_cartographer.intake.session import create_session, record_answer

ROOT = Path(__file__).resolve().parents[1]
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


def _apply(session, plan, *, confirm: bool, start: datetime):
    current = session
    for index, item in enumerate(plan.questions, start=1):
        question = next(q for q in available_questions(current) if q.id == item.question_id)
        asked = start + timedelta(seconds=index * 2)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:11434")
    parser.add_argument("--model", default="qwen2.5-coder:7b")
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=600.0,
        help="HTTP read timeout for each local structured-output call (max 600).",
    )
    parser.add_argument(
        "--output-dir", default=".test-cartographer/sprint-8/live"
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    seed = load_minimal_seed(
        ROOT / "testdata/guided_intake/seed/product_search.json"
    )
    profile = GuidedIntakeProfile(
        id="guided_live_local",
        provider=GuidanceProviderKind.OLLAMA,
        model=args.model,
        base_url=args.base_url,
        timeout_seconds=args.timeout_seconds,
        max_rounds=4,
        allowed_sensitivities=("public", "internal"),
        temperature=0.0,
        seed=42,
    )
    session = create_session(
        build_minimal_context(seed),
        session_id="intake_guided_live",
        started_at=now,
    )
    run = create_guided_run(
        session,
        seed,
        profile,
        run_id="guided_live_reference",
        started_at=now,
    )

    with OllamaGuidanceProvider(profile) as provider:
        print("Preflighting and preloading the local Ollama model...", flush=True)
        version = provider.preflight()
        print("Starting collection planning call (1/2)...", flush=True)
        collection, run = plan_next_phase(
            session,
            run,
            seed,
            profile,
            provider,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        print(
            f"Collection planning call completed in {run.turns[-1].latency_seconds:.2f}s.",
            flush=True,
        )
        print(f"Local Ollama version: {version}")
        print(f"Local model: {args.model}")
        print("Live collection interview order:")
        for index, item in enumerate(collection.questions, start=1):
            print(f"  {index}. {item.question_id}: {item.user_prompt}")
        session = _apply(
            session,
            collection,
            confirm=False,
            start=now + timedelta(seconds=10),
        )

        print("Starting review planning call (2/2)...", flush=True)
        review, run = plan_next_phase(
            session,
            run,
            seed,
            profile,
            provider,
            started_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
        )
        print(
            f"Review planning call completed in {run.turns[-1].latency_seconds:.2f}s.",
            flush=True,
        )
        print("Live confirmation interview order:")
        for index, item in enumerate(review.questions, start=1):
            print(f"  {index}. {item.question_id}: {item.user_prompt}")
        session = _apply(
            session,
            review,
            confirm=True,
            start=now + timedelta(seconds=50),
        )

    run = finish_guided_run(run, session, updated_at=now + timedelta(seconds=90))
    report = assess_guided_intake(session, run)
    if not report.ready_for_guided_discovery:
        raise RuntimeError("live guided intake did not reach discovery readiness")
    if not report.live_provider_used or len(run.turns) != 2:
        raise RuntimeError("expected exactly two real local-provider planning turns")
    if report.full_adaptation_blocker_count == 0:
        raise RuntimeError("technical discovery blockers must remain after Sprint 8")

    target = Path(args.output_dir)
    target.mkdir(parents=True, exist_ok=True)
    save_context(session.context, target / "context.json")
    save_session(session, target / "session.json")
    save_guided_run(run, target / "run.json")
    serialized = (target / "run.json").read_text(encoding="utf-8")
    if seed.initial_request in serialized or ANSWERS["q_application_base_url"] in serialized:
        raise RuntimeError("raw prompt or human answer leaked into the guided run")

    print("Two structured-output planning calls were completed through local Ollama.")
    print("The model ordered and rephrased only allowlisted deterministic questions.")
    print("The model did not answer questions or write context facts.")
    print("Human answers reached discovery readiness after explicit confirmation.")
    print("Raw prompts, raw responses, and the application URL were not persisted in the run.")
    print("Ready for guided process discovery: true")
    print("Full adaptation ready: false")


if __name__ == "__main__":
    main()
