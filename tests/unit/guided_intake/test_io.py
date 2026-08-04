from pathlib import Path

from test_cartographer.guided_intake.engine import create_guided_run
from test_cartographer.guided_intake.io import load_guided_run, save_guided_run

from .conftest import START


def test_guided_run_round_trip_is_deterministic(
    tmp_path: Path, minimal_session, seed, replay_profile
) -> None:
    run = create_guided_run(
        minimal_session,
        seed,
        replay_profile,
        run_id="guided_io_reference",
        started_at=START,
    )
    path = tmp_path / "run.json"
    save_guided_run(run, path)
    first = path.read_bytes()

    loaded = load_guided_run(path)
    save_guided_run(loaded, path)

    assert loaded == run
    assert path.read_bytes() == first
    assert first.endswith(b"\n")
