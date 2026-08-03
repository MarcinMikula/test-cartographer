import hashlib
import shutil
from pathlib import Path

from test_cartographer.cli import main
from test_cartographer.delivery.enums import CodePatchStatus
from test_cartographer.delivery.io import load_application_report, load_code_patch

ROOT = Path(__file__).resolve().parents[2]


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_cli_builds_previews_reviews_and_applies_only_after_acceptance(tmp_path, capsys):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    patch_path = tmp_path / "patch.json"
    application_path = tmp_path / "application.json"
    before = _tree_hash(framework)

    assert main([
        "deliver", "build",
        "--profile", str(ROOT / "testdata/adaptation/profile/qa_automation_framework.json"),
        "--generation-profile", str(ROOT / "testdata/delivery/profile/public_search_generation.json"),
        "--snapshot", str(ROOT / "testdata/adaptation/snapshot/qa_automation_framework.json"),
        "--run", str(ROOT / "testdata/synthesis/run/accepted_public_search.json"),
        "--plan", str(ROOT / "testdata/adaptation/plan/accepted_public_search.json"),
        "--framework-root", str(framework),
        "--patch", str(patch_path),
        "--patch-id", "patch_cli_public_search",
    ]) == 0
    patch = load_code_patch(patch_path)
    assert patch.status is CodePatchStatus.READY_FOR_REVIEW
    output = capsys.readouterr().out
    assert "Generated source included: true" in output
    assert "Framework files were not modified." in output
    assert _tree_hash(framework) == before

    assert main(["deliver", "preview", "--patch", str(patch_path)]) == 0
    preview = capsys.readouterr().out
    assert "===== create_file: pages/catalog_page.py::CatalogPage =====" in preview
    assert "def test_search_catalog" in preview

    assert main([
        "deliver", "review",
        "--patch", str(patch_path),
        "--decision", "accepted",
        "--reason", "Exact generated source reviewed.",
        "--review-seconds", "4.5",
    ]) == 0
    assert load_code_patch(patch_path).status is CodePatchStatus.ACCEPTED
    assert _tree_hash(framework) == before
    capsys.readouterr()

    assert main([
        "deliver", "apply",
        "--profile", str(ROOT / "testdata/adaptation/profile/qa_automation_framework.json"),
        "--snapshot", str(ROOT / "testdata/adaptation/snapshot/qa_automation_framework.json"),
        "--patch", str(patch_path),
        "--framework-root", str(framework),
        "--application", str(application_path),
        "--application-id", "apply_cli_public_search",
    ]) == 0
    report = load_application_report(application_path)
    assert len(report.changes) == 4
    assert (framework / "tests/e2e/test_search_catalog.py").is_file()
    assert "Preflight passed: true" in capsys.readouterr().out


def test_delivery_status_requires_exactly_one_artifact(capsys):
    try:
        main(["deliver", "status"])
    except SystemExit as exc:
        assert exc.code == 2
    assert "provide exactly one" in capsys.readouterr().err
