import hashlib
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.adaptation.scanner import inspect_framework


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def test_inspection_matches_replay_fixture(
    repository_root,
    workspace_profile,
    framework_snapshot,
):
    actual = inspect_framework(
        repository_root / "testdata/framework/reference",
        workspace_profile,
        snapshot_id=framework_snapshot.id,
        captured_at=framework_snapshot.captured_at,
    )
    assert actual == framework_snapshot


def test_inspection_is_read_only(repository_root, workspace_profile):
    root = repository_root / "testdata/framework/reference"
    before = _tree_hash(root)
    inspect_framework(
        root,
        workspace_profile,
        snapshot_id="snapshot_read_only",
        captured_at=datetime.now(timezone.utc),
    )
    assert _tree_hash(root) == before


def test_fingerprint_is_independent_of_capture_time(repository_root, workspace_profile):
    root = repository_root / "testdata/framework/reference"
    first = inspect_framework(
        root,
        workspace_profile,
        snapshot_id="snapshot_first",
        captured_at=datetime(2026, 8, 2, tzinfo=timezone.utc),
    )
    second = inspect_framework(
        root,
        workspace_profile,
        snapshot_id="snapshot_second",
        captured_at=datetime(2026, 8, 3, tzinfo=timezone.utc),
    )
    assert first.root_fingerprint == second.root_fingerprint
    assert first.entries == second.entries


def test_snapshot_contains_symbols_but_not_source_content(framework_snapshot):
    rendered = framework_snapshot.model_dump_json()
    assert "EcommerceSearchPage" in rendered
    assert "search_for" in rendered
    assert "self.page.goto" not in rendered
    assert "pass\\n" not in rendered
    assert "testdata/framework/reference" not in rendered


def test_source_change_changes_fingerprint(tmp_path, repository_root, workspace_profile):
    source = repository_root / "testdata/framework/reference"
    target = tmp_path / "framework"
    shutil.copytree(source, target)
    before = inspect_framework(
        target,
        workspace_profile,
        snapshot_id="snapshot_before",
        captured_at=datetime.now(timezone.utc),
    )
    page = target / "pages/ecommerce_search_page.py"
    page.write_text(page.read_text() + "\nclass AddedPage:\n    pass\n", encoding="utf-8")
    after = inspect_framework(
        target,
        workspace_profile,
        snapshot_id="snapshot_after",
        captured_at=datetime.now(timezone.utc),
    )
    assert before.root_fingerprint != after.root_fingerprint
    changed = next(entry for entry in after.entries if entry.path == "pages/ecommerce_search_page.py")
    assert {symbol.name for symbol in changed.python_symbols} == {
        "AddedPage",
        "EcommerceSearchPage",
    }


def test_missing_root_marker_is_rejected(tmp_path, workspace_profile):
    (tmp_path / "pages").mkdir()
    with pytest.raises(ValueError, match="root marker is missing"):
        inspect_framework(
            tmp_path,
            workspace_profile,
            snapshot_id="snapshot_invalid",
            captured_at=datetime.now(timezone.utc),
        )


def test_file_size_budget_is_enforced(repository_root, workspace_profile):
    constrained = workspace_profile.model_copy(update={"max_file_bytes": 10})
    with pytest.raises(ValueError, match="max_file_bytes"):
        inspect_framework(
            repository_root / "testdata/framework/reference",
            constrained,
            snapshot_id="snapshot_too_large",
            captured_at=datetime.now(timezone.utc),
        )
