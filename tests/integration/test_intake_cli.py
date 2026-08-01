from datetime import datetime, timedelta, timezone
from pathlib import Path

from test_cartographer.cli import main, run_intake_loop
from test_cartographer.context.io import load_context
from test_cartographer.intake.enums import IntakeSessionState
from test_cartographer.intake.io import load_session, save_session
from test_cartographer.intake.session import create_session

ROOT = Path(__file__).resolve().parents[2]
START = datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc)


def _source_context() -> Path:
    return ROOT / "testdata" / "context" / "incomplete" / "public_search_flow.json"


def test_cli_start_status_and_export(tmp_path: Path, capsys) -> None:
    session_path = tmp_path / "session.json"
    exported_path = tmp_path / "context.json"

    assert main(
        [
            "intake",
            "start",
            "--context",
            str(_source_context()),
            "--session",
            str(session_path),
            "--session-id",
            "intake_reference",
        ]
    ) == 0
    assert main(["intake", "status", "--session", str(session_path)]) == 0
    assert main(
        [
            "intake",
            "export",
            "--session",
            str(session_path),
            "--context",
            str(exported_path),
        ]
    ) == 0

    output = capsys.readouterr().out
    assert "Created intake session" in output
    assert "Next question: q_process_risk" in output
    assert load_context(exported_path).id == "ctx_public_catalog_search_incomplete"


def test_interactive_loop_completes_human_intake_and_records_effort(
    tmp_path: Path,
) -> None:
    session_path = tmp_path / "session.json"
    session = create_session(
        load_context(_source_context()),
        session_id="intake_reference",
        started_at=START,
    )
    save_session(session, session_path)

    answers = iter(
        [
            "Search failures can hide relevant catalog items.",
            "Matching items are shown in the visible results list.",
            "An item title contains the query case-insensitively.",
            ":confirm",
            ":confirm",
        ]
    )
    times = iter(START + timedelta(seconds=value) for value in range(1, 11))
    timers = iter(float(value) for value in range(10))
    output: list[str] = []

    completed = run_intake_loop(
        session_path,
        input_fn=lambda _prompt: next(answers),
        output_fn=output.append,
        now_fn=lambda: next(times),
        timer_fn=lambda: next(timers),
    )

    assert completed.state is IntakeSessionState.COMPLETE
    assert completed.metrics.active_seconds == 5.0
    assert completed.metrics.confirmed_count == 2
    assert load_session(session_path) == completed
    assert any("Full adaptation blockers: 1" in line for line in output)


def test_quit_pauses_session(tmp_path: Path) -> None:
    session_path = tmp_path / "session.json"
    session = create_session(
        load_context(_source_context()),
        session_id="intake_reference",
        started_at=START,
    )
    save_session(session, session_path)
    times = iter((START + timedelta(seconds=1), START + timedelta(seconds=2)))
    timers = iter((0.0, 0.5))

    paused = run_intake_loop(
        session_path,
        input_fn=lambda _prompt: ":quit",
        output_fn=lambda _message: None,
        now_fn=lambda: next(times),
        timer_fn=lambda: next(timers),
    )

    assert paused.state is IntakeSessionState.PAUSED
    assert paused.interactions == ()
