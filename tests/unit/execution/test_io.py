from test_cartographer.execution.io import (
    load_execution_bundle,
    load_execution_profile,
    save_execution_bundle,
    save_execution_profile,
)


def test_execution_profile_round_trips(tmp_path, execution_profile):
    target = tmp_path / "profile.json"
    save_execution_profile(execution_profile, target)
    assert load_execution_profile(target) == execution_profile


def test_execution_bundle_round_trips(tmp_path, execution_bundle):
    target = tmp_path / "bundle.json"
    save_execution_bundle(execution_bundle, target)
    assert load_execution_bundle(target) == execution_bundle
