import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.delivery.apply import apply_code_patch

ROOT = Path(__file__).resolve().parents[3]


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_apply_writes_all_accepted_changes_after_preflight(
    tmp_path,
    accepted_patch,
    workspace_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    values = iter([10.0, 10.75])
    report = apply_code_patch(
        accepted_patch,
        workspace_profile,
        framework_snapshot,
        framework,
        application_id="apply_test_public_search",
        applied_at=datetime(2026, 8, 2, 13, 20, tzinfo=timezone.utc),
        timer_fn=lambda: next(values),
    )
    assert report.application_seconds == 0.75
    assert len(report.changes) == 4
    assert (framework / "pages/catalog_page.py").is_file()
    assert (framework / "components/catalog_search_form.py").is_file()
    assert (framework / "tests/e2e/test_search_catalog.py").is_file()
    conftest = (framework / "tests/e2e/conftest.py").read_text(encoding="utf-8")
    assert "def catalog_context" in conftest
    assert report.verification_pending is True
    assert report.target_root_persisted is False


def test_apply_requires_accepted_patch(
    tmp_path,
    pending_patch,
    workspace_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    with pytest.raises(ValueError, match="human-accepted"):
        apply_code_patch(
            pending_patch,
            workspace_profile,
            framework_snapshot,
            framework,
            application_id="apply_pending",
            applied_at=datetime(2026, 8, 2, 13, 20, tzinfo=timezone.utc),
        )


def test_apply_rejects_drift_before_any_write(
    tmp_path,
    accepted_patch,
    workspace_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    (framework / "tests/e2e/conftest.py").write_text("# drift\n", encoding="utf-8")
    before = _tree_hash(framework)
    with pytest.raises(ValueError, match="fingerprint changed"):
        apply_code_patch(
            accepted_patch,
            workspace_profile,
            framework_snapshot,
            framework,
            application_id="apply_drift",
            applied_at=datetime(2026, 8, 2, 13, 20, tzinfo=timezone.utc),
        )
    assert _tree_hash(framework) == before
    assert not (framework / "pages/catalog_page.py").exists()


def test_apply_rejects_target_outside_allowlist(
    tmp_path,
    accepted_patch,
    workspace_profile,
    framework_snapshot,
):
    framework = tmp_path / "framework"
    shutil.copytree(ROOT / "testdata/framework/reference", framework)
    payload = accepted_patch.model_dump(mode="json")
    payload["changes"][0]["target_path"] = "docs/catalog_page.py"
    from test_cartographer.delivery.models import CodePatch

    modified = CodePatch.model_validate(payload)
    with pytest.raises(ValueError, match="outside workspace allowlist"):
        apply_code_patch(
            modified,
            workspace_profile,
            framework_snapshot,
            framework,
            application_id="apply_outside",
            applied_at=datetime(2026, 8, 2, 13, 20, tzinfo=timezone.utc),
        )
