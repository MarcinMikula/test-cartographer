"""Deterministic JSON persistence for human-guided intake sessions."""

from pathlib import Path

from test_cartographer.intake.models import IntakeSession


def load_session(path: str | Path) -> IntakeSession:
    session_path = Path(path)
    return IntakeSession.model_validate_json(session_path.read_text(encoding="utf-8"))


def save_session(session: IntakeSession, path: str | Path) -> None:
    session_path = Path(path)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = session.model_dump_json(indent=2, exclude_none=False)
    session_path.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
