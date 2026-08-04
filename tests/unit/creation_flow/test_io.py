from test_cartographer.creation_flow.io import load_creation_flow_run, save_creation_flow_run


def test_creation_flow_round_trip(tmp_path, passed_creation_run) -> None:
    target = tmp_path / "run.json"
    save_creation_flow_run(passed_creation_run, target)
    assert load_creation_flow_run(target) == passed_creation_run
