from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.delivery.sandbox import materialize_snapshot_sandbox


def _build_source(root: Path) -> None:
    (root / "pages").mkdir(parents=True)
    (root / "components").mkdir()
    (root / "tests/e2e").mkdir(parents=True)
    (root / "testdata").mkdir()
    (root / "README.md").write_text("reference\n", encoding="utf-8")
    (root / "requirements.txt").write_text("pytest\n", encoding="utf-8")
    (root / "pages/base_page.py").write_text("class BasePage:\n    pass\n", encoding="utf-8")
    (root / "components/base_component.py").write_text("class BaseComponent:\n    pass\n", encoding="utf-8")
    (root / "tests/e2e/__init__.py").write_text("", encoding="utf-8")
    (root / "testdata/settings.py").write_text("TIMEOUT = 1\n", encoding="utf-8")


def test_materializer_copies_only_snapshot_approved_files(tmp_path, workspace_profile) -> None:
    source = tmp_path / "source"
    _build_source(source)
    (source / "tests/conftest.py").write_text(
        "raise ImportError('out-of-scope parent conftest must not load')\n",
        encoding="utf-8",
    )
    snapshot = inspect_framework(
        source,
        workspace_profile,
        snapshot_id="snapshot_materialize",
        captured_at=datetime(2026, 8, 2, 20, 0, tzinfo=timezone.utc),
    )

    target = tmp_path / "sandbox"
    copied = materialize_snapshot_sandbox(source, target, workspace_profile, snapshot)

    assert copied == sum(entry.kind.value == "file" for entry in snapshot.entries)
    assert (target / "pages/base_page.py").is_file()
    assert not (target / "tests/conftest.py").exists()
    replay = inspect_framework(
        target,
        workspace_profile,
        snapshot_id="snapshot_replay",
        captured_at=datetime(2026, 8, 2, 20, 1, tzinfo=timezone.utc),
    )
    assert replay.root_fingerprint == snapshot.root_fingerprint


def test_materializer_rejects_stale_source_and_removes_partial_target(tmp_path, workspace_profile) -> None:
    source = tmp_path / "source"
    _build_source(source)
    snapshot = inspect_framework(
        source,
        workspace_profile,
        snapshot_id="snapshot_stale",
        captured_at=datetime(2026, 8, 2, 20, 0, tzinfo=timezone.utc),
    )
    (source / "pages/base_page.py").write_text("class Changed:\n    pass\n", encoding="utf-8")
    target = tmp_path / "sandbox"

    with pytest.raises(ValueError, match="fingerprint changed"):
        materialize_snapshot_sandbox(source, target, workspace_profile, snapshot)

    assert not target.exists()


def test_materializer_rejects_non_empty_target(tmp_path, workspace_profile) -> None:
    source = tmp_path / "source"
    _build_source(source)
    snapshot = inspect_framework(
        source,
        workspace_profile,
        snapshot_id="snapshot_target",
        captured_at=datetime(2026, 8, 2, 20, 0, tzinfo=timezone.utc),
    )
    target = tmp_path / "sandbox"
    target.mkdir()
    (target / "unexpected.txt").write_text("unexpected", encoding="utf-8")

    with pytest.raises(ValueError, match="absent or empty"):
        materialize_snapshot_sandbox(source, target, workspace_profile, snapshot)
