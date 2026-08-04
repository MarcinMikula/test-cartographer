"""Orchestration and validation for one guided-intake planning phase."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from test_cartographer.guided_intake.enums import (
    GuidanceProviderKind,
    GuidedIntakePhase,
    GuidedIntakeRunState,
)
from test_cartographer.guided_intake.models import (
    GuidedIntakeProfile,
    GuidedIntakeRun,
    GuidedIntakeTurn,
    GuidedInterviewPlan,
)
from test_cartographer.guided_intake.parser import parse_guided_plan
from test_cartographer.guided_intake.prompt import (
    build_guidance_request,
    render_guidance_prompt,
)
from test_cartographer.guided_intake.provider import GuidanceProvider
from test_cartographer.intake.models import IntakeQuestion, IntakeSession
from test_cartographer.intake.rules import list_questions
from test_cartographer.intake.seed import MinimalContextSeed


def create_guided_run(
    session: IntakeSession,
    seed: MinimalContextSeed,
    profile: GuidedIntakeProfile,
    *,
    run_id: str,
    started_at: datetime,
) -> GuidedIntakeRun:
    return GuidedIntakeRun(
        id=run_id,
        profile_id=profile.id,
        seed_id=seed.id,
        session_id=session.id,
        context_id=session.context.id,
        state=GuidedIntakeRunState.ACTIVE,
        started_at=started_at,
        updated_at=started_at,
    )


def available_questions(session: IntakeSession) -> tuple[IntakeQuestion, ...]:
    deferred = set(session.deferred_question_ids)
    return tuple(
        question
        for question in list_questions(session.context)
        if question.id not in deferred
    )


def phase_for_questions(questions: tuple[IntakeQuestion, ...]) -> GuidedIntakePhase:
    if all(question.current_value is not None for question in questions):
        return GuidedIntakePhase.REVIEW
    return GuidedIntakePhase.COLLECTION


def plan_next_phase(
    session: IntakeSession,
    run: GuidedIntakeRun,
    seed: MinimalContextSeed,
    profile: GuidedIntakeProfile,
    provider: GuidanceProvider,
    *,
    started_at: datetime,
    completed_at: datetime | None = None,
) -> tuple[GuidedInterviewPlan, GuidedIntakeRun]:
    questions = available_questions(session)
    if not questions:
        raise ValueError("no guided-intake questions are currently available")
    if len(run.turns) >= profile.max_rounds:
        raise ValueError("guided intake exceeded the configured round budget")
    phase = phase_for_questions(questions)
    request = build_guidance_request(
        session.context,
        seed,
        questions,
        profile,
        phase=phase,
    )
    prompt = render_guidance_prompt(request)
    result = provider.plan(request, prompt)
    turn_completed_at = completed_at or datetime.now(timezone.utc)
    plan = parse_guided_plan(result.raw_output)
    _validate_plan(plan, questions, phase)

    provider_kind = profile.provider
    turn = GuidedIntakeTurn(
        sequence=len(run.turns) + 1,
        phase=phase,
        provider=provider_kind,
        model=result.model,
        candidate_question_ids=tuple(item.id for item in questions),
        planned_question_ids=tuple(item.question_id for item in plan.questions),
        started_at=started_at,
        completed_at=turn_completed_at,
        latency_seconds=result.latency_seconds,
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        response_sha256=hashlib.sha256(result.raw_output.encode("utf-8")).hexdigest(),
        prompt_characters=len(prompt),
        response_characters=len(result.raw_output),
    )
    updated = run.model_copy(
        update={
            "updated_at": turn_completed_at,
            "turns": (*run.turns, turn),
            "live_provider_used": (
                run.live_provider_used
                or provider_kind is GuidanceProviderKind.OLLAMA
            ),
        }
    )
    return plan, GuidedIntakeRun.model_validate(updated.model_dump(mode="python"))


def finish_guided_run(
    run: GuidedIntakeRun,
    session: IntakeSession,
    *,
    updated_at: datetime,
) -> GuidedIntakeRun:
    questions = available_questions(session)
    if questions:
        state = GuidedIntakeRunState.ACTIVE
    elif session.state.value == "complete":
        state = GuidedIntakeRunState.COMPLETE
    else:
        state = GuidedIntakeRunState.BLOCKED
    updated = run.model_copy(update={"state": state, "updated_at": updated_at})
    return GuidedIntakeRun.model_validate(updated.model_dump(mode="python"))


def _validate_plan(
    plan: GuidedInterviewPlan,
    questions: tuple[IntakeQuestion, ...],
    phase: GuidedIntakePhase,
) -> None:
    expected = {question.id for question in questions}
    actual = {item.question_id for item in plan.questions}
    if plan.phase is not phase:
        raise ValueError("guided plan phase does not match the current intake phase")
    if actual != expected or len(plan.questions) != len(questions):
        raise ValueError("guided plan must contain every available question exactly once")
    for item in plan.questions:
        if len(item.user_prompt) > 500:
            raise ValueError("guided user prompt exceeds 500 characters")
        rendered = f"{item.user_prompt} {item.reason}".casefold()
        forbidden = ("password", "token", "cookie", "secret", "credential")
        if any(term in rendered for term in forbidden):
            raise ValueError("guided plan requests prohibited sensitive information")
