from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.context.io import load_context
from test_cartographer.intake.io import load_session, save_session
from test_cartographer.intake.session import create_session

ROOT = Path(__file__).resolve().parents[3]


def test_session_round_trip_is_deterministic(tmp_path: Path) -> None:
    context = load_context(
        ROOT / "testdata" / "context" / "incomplete" / "public_search_flow.json"
    )
    session = create_session(
        context,
        session_id="intake_reference",
        started_at=datetime(2026, 8, 1, 12, 0, tzinfo=timezone.utc),
    )
    path = tmp_path / "session.json"

    save_session(session, path)
    first = path.read_bytes()
    loaded = load_session(path)
    save_session(loaded, path)

    assert loaded == session
    assert path.read_bytes() == first
    assert first.endswith(b"\n")
