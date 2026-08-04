from test_cartographer.discovery.io import (
    load_discovery_plan,
    load_discovery_profile,
    save_discovery_plan,
    save_discovery_profile,
)


def test_profile_round_trip(tmp_path, profile) -> None:
    path = tmp_path / "profile.json"
    save_discovery_profile(profile, path)
    assert load_discovery_profile(path) == profile


def test_plan_round_trip(tmp_path, plan) -> None:
    path = tmp_path / "plan.json"
    save_discovery_plan(plan, path)
    assert load_discovery_plan(path) == plan
