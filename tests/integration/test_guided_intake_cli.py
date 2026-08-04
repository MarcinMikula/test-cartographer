from pathlib import Path

from test_cartographer.cli import main
from test_cartographer.context.io import load_context
from test_cartographer.intake.io import load_session

ROOT = Path(__file__).resolve().parents[2]


def test_cli_creates_minimal_context_and_session(tmp_path: Path, capsys) -> None:
    context_path = tmp_path / "context.json"
    session_path = tmp_path / "session.json"

    result = main(
        [
            "intake",
            "seed",
            "--seed",
            str(ROOT / "testdata/guided_intake/seed/product_search.json"),
            "--context",
            str(context_path),
            "--session",
            str(session_path),
            "--session-id",
            "intake_cli_guided",
        ]
    )

    assert result == 0
    assert load_context(context_path).id == "ctx_product_search_minimal"
    assert load_session(session_path).id == "intake_cli_guided"
    assert "Human-intake blockers: 9" in capsys.readouterr().out


def test_cli_shows_discovery_readiness_for_completed_replay(capsys) -> None:
    result = main(
        [
            "intake",
            "guide-status",
            "--session",
            str(ROOT / "testdata/guided_intake/session/replay_complete.json"),
            "--run",
            str(ROOT / "testdata/guided_intake/run/replay_complete.json"),
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert "Ready for guided discovery: true" in output
    assert "Full adaptation blockers:" in output
    assert "Raw prompts persisted: false" in output
