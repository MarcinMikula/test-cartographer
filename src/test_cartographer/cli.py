"""Command-line entry point for the deterministic TestCartographer intake."""

from __future__ import annotations

import argparse
import sys
import time
import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path

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

InputFn = Callable[[str], str]
OutputFn = Callable[[str], None]
NowFn = Callable[[], datetime]
TimerFn = Callable[[], float]


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "intake":
        parser.error("a command is required")

    if args.intake_command == "start":
        return _start_command(args)
    if args.intake_command == "run":
        return _run_command(args)
    if args.intake_command == "status":
        return _status_command(args)
    if args.intake_command == "export":
        return _export_command(args)

    parser.error("an intake command is required")
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

    output_fn(_format_status(session))

    while True:
        question = select_next_question(
            session.context,
            excluded_question_ids=session.deferred_question_ids,
        )
        if question is None:
            output_fn(_format_status(session))
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
            output_fn(_format_status(session))
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

    return parser


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
    print(_format_status(session))
    return 0


def _run_command(args: argparse.Namespace) -> int:
    run_intake_loop(args.session, retry_deferred=args.retry_deferred)
    return 0


def _status_command(args: argparse.Namespace) -> int:
    print(_format_status(load_session(args.session)))
    return 0


def _export_command(args: argparse.Namespace) -> int:
    session = load_session(args.session)
    save_context(session.context, args.context)
    print(f"Exported context: {args.context}")
    print(_format_status(session))
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


def _format_status(session: IntakeSession) -> str:
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


if __name__ == "__main__":
    sys.exit(main())
