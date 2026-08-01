"""Command-line entry point for deterministic intake and browser observation."""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.context.io import load_context, save_context
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.intake.enums import IntakeAnswerAction, IntakeSessionState
from test_cartographer.intake.io import load_session, save_session
from test_cartographer.intake.models import IntakeAnswer, IntakeQuestion, IntakeSession
from test_cartographer.intake.rules import assess_intake, select_next_question
from test_cartographer.intake.session import (
    create_session,
    pause_session,
    record_answer,
    resume_session,
)
from test_cartographer.observation.capture import capture_browser_observation
from test_cartographer.observation.enums import ObservationDecision
from test_cartographer.observation.io import load_observation, save_observation
from test_cartographer.observation.models import BrowserObservation
from test_cartographer.observation.review import (
    apply_accepted_observation,
    review_observation,
)

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
NowFn = Callable[[], datetime]
TimerFn = Callable[[], float]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "intake":
        return _dispatch_intake(parser, args)
    if args.command == "observe":
        return _dispatch_observation(parser, args)

    parser.error("a command is required")
    return 2


def run_intake_loop(
    session_path: str | Path,
    *,
    retry_deferred: bool = False,
    input_fn: InputFn = input,
    output_fn: OutputFn = print,
    now_fn: NowFn = lambda: datetime.now(timezone.utc),
    timer_fn: TimerFn = time.perf_counter,
) -> IntakeSession:
    """Run and persist an interactive intake session after every action."""

    path = Path(session_path)
    session = load_session(path)
    if session.state is IntakeSessionState.PAUSED or retry_deferred:
        session = resume_session(
            session,
            updated_at=now_fn(),
            retry_deferred=retry_deferred,
        )
        save_session(session, path)

    output_fn(_format_intake_status(session))

    while True:
        question = select_next_question(
            session.context,
            excluded_question_ids=session.deferred_question_ids,
        )
        if question is None:
            output_fn(_format_intake_status(session))
            return session

        _print_question(question, output_fn)
        asked_at = now_fn()
        started = timer_fn()
        try:
            raw = input_fn("> ").strip()
        except (EOFError, KeyboardInterrupt):
            raw = ":quit"
        active_seconds = max(0.0, timer_fn() - started)
        answered_at = now_fn()

        if raw == ":quit":
            session = pause_session(session, updated_at=answered_at)
            save_session(session, path)
            output_fn("Intake paused. The session can be resumed later.")
            output_fn(_format_intake_status(session))
            return session

        try:
            answer = _parse_answer(raw, question)
        except ValueError as exc:
            output_fn(f"Invalid answer: {exc}")
            continue

        session = record_answer(
            session,
            question=question,
            answer=answer,
            asked_at=asked_at,
            answered_at=answered_at,
            active_seconds=active_seconds,
        )
        save_session(session, path)
        output_fn(f"Saved: {question.target_path} ({answer.action.value}).")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="test-cartographer")
    commands = parser.add_subparsers(dest="command")

    intake = commands.add_parser("intake", help="collect human process context")
    intake_commands = intake.add_subparsers(dest="intake_command")

    start = intake_commands.add_parser("start", help="create an intake session")
    start.add_argument("--context", required=True, type=Path)
    start.add_argument("--session", required=True, type=Path)
    start.add_argument("--session-id")

    run = intake_commands.add_parser("run", help="run or resume intake")
    run.add_argument("--session", required=True, type=Path)
    run.add_argument(
        "--retry-deferred",
        action="store_true",
        help="ask previously skipped or unknown questions again",
    )

    status = intake_commands.add_parser("status", help="show intake status")
    status.add_argument("--session", required=True, type=Path)

    export = intake_commands.add_parser("export", help="export current context")
    export.add_argument("--session", required=True, type=Path)
    export.add_argument("--context", required=True, type=Path)

    observe = commands.add_parser(
        "observe",
        help="capture and review one bounded browser observation",
    )
    observe_commands = observe.add_subparsers(dest="observe_command")

    capture = observe_commands.add_parser(
        "capture",
        help="open one page and capture one selected element",
    )
    capture.add_argument("--context", required=True, type=Path)
    capture.add_argument("--url", required=True)
    capture.add_argument("--element-id", required=True)
    capture.add_argument("--observation", required=True, type=Path)
    capture.add_argument("--observation-id")
    capture.add_argument(
        "--sensitivity",
        choices=[level.value for level in SensitivityLevel],
        default=SensitivityLevel.INTERNAL.value,
    )
    capture.add_argument("--headed", action="store_true")
    capture.add_argument("--timeout-ms", type=int, default=10_000)
    capture.add_argument("--executable-path")

    observation_status = observe_commands.add_parser(
        "status",
        help="show one observation and review status",
    )
    observation_status.add_argument("--observation", required=True, type=Path)

    review = observe_commands.add_parser(
        "review",
        help="accept or reject a pending observation",
    )
    review.add_argument("--observation", required=True, type=Path)
    review.add_argument(
        "--decision",
        required=True,
        choices=[ObservationDecision.ACCEPTED.value, ObservationDecision.REJECTED.value],
    )
    review.add_argument("--reason")
    review.add_argument("--review-seconds", type=float, default=0.0)
    review.add_argument("--context", type=Path)
    review.add_argument("--output-context", type=Path)

    return parser


def _dispatch_intake(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
) -> int:
    if args.intake_command == "start":
        return _start_command(args)
    if args.intake_command == "run":
        return _run_command(args)
    if args.intake_command == "status":
        return _intake_status_command(args)
    if args.intake_command == "export":
        return _export_command(args)
    parser.error("an intake command is required")
    return 2


def _dispatch_observation(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
) -> int:
    if args.observe_command == "capture":
        return _capture_command(args)
    if args.observe_command == "status":
        return _observation_status_command(args)
    if args.observe_command == "review":
        return _review_command(parser, args)
    parser.error("an observe command is required")
    return 2


def _start_command(args: argparse.Namespace) -> int:
    context = load_context(args.context)
    session_id = args.session_id or f"intake_{uuid.uuid4().hex[:12]}"
    session = create_session(
        context,
        session_id=session_id,
        started_at=datetime.now(timezone.utc),
    )
    save_session(session, args.session)
    print(f"Created intake session: {args.session}")
    print(_format_intake_status(session))
    return 0


def _run_command(args: argparse.Namespace) -> int:
    run_intake_loop(args.session, retry_deferred=args.retry_deferred)
    return 0


def _intake_status_command(args: argparse.Namespace) -> int:
    print(_format_intake_status(load_session(args.session)))
    return 0


def _export_command(args: argparse.Namespace) -> int:
    session = load_session(args.session)
    save_context(session.context, args.context)
    print(f"Exported context: {args.context}")
    print(_format_intake_status(session))
    return 0


def _capture_command(args: argparse.Namespace) -> int:
    context = load_context(args.context)
    observation_id = args.observation_id or f"obs_{uuid.uuid4().hex[:12]}"
    observation = capture_browser_observation(
        context,
        url=args.url,
        element_id=args.element_id,
        observation_id=observation_id,
        captured_at=datetime.now(timezone.utc),
        sensitivity=SensitivityLevel(args.sensitivity),
        headless=not args.headed,
        timeout_ms=args.timeout_ms,
        executable_path=args.executable_path,
    )
    save_observation(observation, args.observation)
    print(f"Captured observation: {args.observation}")
    print(_format_observation_status(observation))
    return 0


def _observation_status_command(args: argparse.Namespace) -> int:
    print(_format_observation_status(load_observation(args.observation)))
    return 0


def _review_command(
    parser: argparse.ArgumentParser,
    args: argparse.Namespace,
) -> int:
    decision = ObservationDecision(args.decision)
    if decision is ObservationDecision.REJECTED and not args.reason:
        parser.error("--reason is required when rejecting an observation")
    if decision is ObservationDecision.ACCEPTED:
        if args.context is None or args.output_context is None:
            parser.error(
                "accepted observation requires --context and --output-context"
            )

    observation = load_observation(args.observation)
    reviewed = review_observation(
        observation,
        decision=decision,
        reviewed_at=datetime.now(timezone.utc),
        reason=args.reason,
        review_seconds=args.review_seconds,
    )
    save_observation(reviewed, args.observation)
    print(f"Reviewed observation: {args.observation}")
    print(_format_observation_status(reviewed))

    if decision is ObservationDecision.ACCEPTED:
        context = load_context(args.context)
        updated = apply_accepted_observation(context, reviewed)
        save_context(updated, args.output_context)
        readiness = assess_readiness(updated)
        print(f"Updated context: {args.output_context}")
        print(f"Full adaptation blockers: {readiness.blocker_count}")
        print(f"Full adaptation warnings: {readiness.warning_count}")
        print(f"Full adaptation ready: {str(readiness.ready).lower()}")
    else:
        print("Context was not changed.")
    return 0


def _parse_answer(raw: str, question: IntakeQuestion) -> IntakeAnswer:
    if not raw:
        raise ValueError("enter a value or one of the displayed commands")
    command_map = {
        ":confirm": IntakeAnswerAction.CONFIRM,
        ":unknown": IntakeAnswerAction.UNKNOWN,
        ":skip": IntakeAnswerAction.SKIP,
    }
    if raw.startswith(":"):
        action = command_map.get(raw)
        if action is None:
            raise ValueError("supported commands are :confirm, :unknown, :skip, :quit")
        if action not in question.allowed_actions:
            raise ValueError(f"{raw} is not allowed for this question")
        return IntakeAnswer(action=action)
    return IntakeAnswer(action=IntakeAnswerAction.PROVIDE, value=raw)


def _print_question(question: IntakeQuestion, output_fn: OutputFn) -> None:
    output_fn("")
    output_fn(question.prompt)
    if question.current_value is not None:
        output_fn(f"Current value: {question.current_value}")
    commands = [":unknown", ":skip", ":quit"]
    if IntakeAnswerAction.CONFIRM in question.allowed_actions:
        commands.insert(0, ":confirm")
    output_fn(f"Commands: {', '.join(commands)}")


def _format_intake_status(session: IntakeSession) -> str:
    intake = assess_intake(session.context)
    adaptation = assess_readiness(session.context)
    metrics = session.metrics
    next_question = select_next_question(
        session.context,
        excluded_question_ids=session.deferred_question_ids,
    )
    next_label = next_question.id if next_question is not None else "none"
    return "\n".join(
        (
            f"Session: {session.id}",
            f"State: {session.state.value}",
            f"Human-intake blockers: {intake.blocker_count}",
            f"Human-intake warnings: {intake.warning_count}",
            f"Full adaptation blockers: {adaptation.blocker_count}",
            f"Next question: {next_label}",
            f"Interactions: {metrics.interaction_count}",
            f"Provided: {metrics.provided_count}",
            f"Confirmed: {metrics.confirmed_count}",
            f"Unknown: {metrics.unknown_count}",
            f"Skipped: {metrics.skipped_count}",
            f"Active seconds: {metrics.active_seconds:.3f}",
        )
    )


def _format_observation_status(observation: BrowserObservation) -> str:
    attributes = ", ".join(
        f"{item.name.value}={item.value}" for item in observation.element.attributes
    ) or "none"
    return "\n".join(
        (
            f"Observation: {observation.id}",
            f"Decision: {observation.decision.value}",
            f"Context: {observation.context_id}",
            f"Target element: {observation.target_element_id}",
            f"Target locator: {observation.target_locator_id}",
            f"Source URL: {observation.source_url}",
            f"Locator: {observation.locator.strategy.value}={observation.locator.value}",
            f"Match count: {observation.locator.match_count}",
            f"Visible: {str(observation.element.visible).lower()}",
            f"Enabled: {str(observation.element.enabled).lower()}",
            f"Editable: {str(observation.element.editable).lower()}",
            f"Observed attributes: {attributes}",
            f"Capture seconds: {observation.capture_seconds:.3f}",
            f"Review seconds: {observation.review_seconds:.3f}",
            f"User actions: {observation.user_action_count}",
            "Raw page persisted: false",
            "Screenshot persisted: false",
            "Input value persisted: false",
            "Text content persisted: false",
            "HTML persisted: false",
        )
    )


if __name__ == "__main__":
    sys.exit(main())
