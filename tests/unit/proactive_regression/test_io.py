from test_cartographer.proactive_regression.io import (
    load_proactive_run,
    save_proactive_run,
)


def test_run_round_trip_is_deterministic(tmp_path, passed_run) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    save_proactive_run(passed_run, first)
    save_proactive_run(load_proactive_run(first), second)
    assert first.read_bytes() == second.read_bytes()


def test_saved_run_contains_no_raw_page_fields(tmp_path, passed_run) -> None:
    path = tmp_path / "run.json"
    save_proactive_run(passed_run, path)
    text = path.read_text(encoding="utf-8")
    assert "page_content" not in text
    assert '"raw_page_persisted": false' in text
