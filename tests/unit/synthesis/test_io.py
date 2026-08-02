from datetime import datetime, timezone

from test_cartographer.synthesis.adapter import ReplaySynthesisAdapter
from test_cartographer.synthesis.io import (
    load_synthesis_request,
    load_synthesis_run,
    save_synthesis_request,
    save_synthesis_run,
)
from test_cartographer.synthesis.pipeline import run_synthesis


def test_request_round_trip_is_deterministic(tmp_path, synthesis_request) -> None:
    target = tmp_path / "request.json"
    save_synthesis_request(synthesis_request, target)
    loaded = load_synthesis_request(target)

    assert loaded == synthesis_request
    assert target.read_text(encoding="utf-8").endswith("\n")


def test_run_round_trip_preserves_raw_output(
    tmp_path,
    synthesis_request,
    valid_raw_output,
) -> None:
    run = run_synthesis(
        synthesis_request,
        ReplaySynthesisAdapter(valid_raw_output),
        run_id="synrun_round_trip",
        started_at=datetime(2026, 8, 2, 13, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 8, 2, 13, 0, 1, tzinfo=timezone.utc),
    )
    target = tmp_path / "run.json"
    save_synthesis_run(run, target)
    loaded = load_synthesis_run(target)

    assert loaded == run
    assert loaded.raw_output == valid_raw_output
    assert target.read_text(encoding="utf-8").endswith("\n")
