import hashlib
import shutil
from pathlib import Path

from test_cartographer.adaptation.enums import AdaptationPlanStatus
from test_cartographer.adaptation.io import (
    load_adaptation_plan,
    load_framework_snapshot,
)
from test_cartographer.cli import main

ROOT = Path(__file__).resolve().parents[2]


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_cli_inspects_plans_and_accepts_without_modifying_framework(
    tmp_path,
    capsys,
) -> None:
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    snapshot_path = tmp_path / "snapshot.json"
    plan_path = tmp_path / "plan.json"
    before = _tree_hash(framework)

    assert (
        main(
            [
                "adapt",
                "inspect",
                "--profile",
                str(ROOT / "testdata/adaptation/profile/qa_automation_framework.json"),
                "--framework-root",
                str(framework),
                "--snapshot",
                str(snapshot_path),
                "--snapshot-id",
                "snapshot_cli_reference",
            ]
        )
        == 0
    )
    snapshot = load_framework_snapshot(snapshot_path)
    assert snapshot.source_contents_persisted is False
    output = capsys.readouterr().out
    assert "Source contents persisted: false" in output
    assert _tree_hash(framework) == before

    assert (
        main(
            [
                "adapt",
                "plan",
                "--profile",
                str(ROOT / "testdata/adaptation/profile/qa_automation_framework.json"),
                "--snapshot",
                str(snapshot_path),
                "--run",
                str(ROOT / "testdata/synthesis/run/accepted_public_search.json"),
                "--plan",
                str(plan_path),
                "--plan-id",
                "adapt_cli_public_search",
            ]
        )
        == 0
    )
    plan = load_adaptation_plan(plan_path)
    assert plan.status is AdaptationPlanStatus.READY_FOR_REVIEW
    output = capsys.readouterr().out
    assert "Framework files modified: false" in output
    assert "Generated source included: false" in output
    assert _tree_hash(framework) == before

    assert main(["adapt", "status", "--plan", str(plan_path)]) == 0
    assert "Decision: pending" in capsys.readouterr().out

    assert (
        main(
            [
                "adapt",
                "review",
                "--plan",
                str(plan_path),
                "--decision",
                "accepted",
                "--reason",
                "Exact targets match the framework architecture.",
                "--review-seconds",
                "3.5",
            ]
        )
        == 0
    )
    accepted = load_adaptation_plan(plan_path)
    assert accepted.status is AdaptationPlanStatus.ACCEPTED
    output = capsys.readouterr().out
    assert "Status: accepted" in output
    assert "Framework files were not modified." in output
    assert _tree_hash(framework) == before


def test_cli_status_requires_exactly_one_artifact(tmp_path, capsys):
    try:
        main(["adapt", "status"])
    except SystemExit as exc:
        assert exc.code == 2
    assert "provide exactly one" in capsys.readouterr().err
