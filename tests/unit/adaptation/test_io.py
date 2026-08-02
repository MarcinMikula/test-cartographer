from test_cartographer.adaptation.io import (
    load_adaptation_plan,
    load_framework_snapshot,
    load_workspace_profile,
    save_adaptation_plan,
    save_framework_snapshot,
    save_workspace_profile,
)


def test_adaptation_contracts_round_trip(tmp_path, workspace_profile, framework_snapshot, repository_root):
    plan = load_adaptation_plan(
        repository_root / "testdata/adaptation/plan/pending_public_search.json"
    )
    profile_path = tmp_path / "profile.json"
    snapshot_path = tmp_path / "snapshot.json"
    plan_path = tmp_path / "plan.json"
    save_workspace_profile(workspace_profile, profile_path)
    save_framework_snapshot(framework_snapshot, snapshot_path)
    save_adaptation_plan(plan, plan_path)
    assert load_workspace_profile(profile_path) == workspace_profile
    assert load_framework_snapshot(snapshot_path) == framework_snapshot
    assert load_adaptation_plan(plan_path) == plan
