"""Materialize an exact framework sandbox from an accepted structural snapshot."""

from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import RepositoryEntryKind
from test_cartographer.adaptation.models import FrameworkSnapshot, WorkspaceProfile
from test_cartographer.adaptation.scanner import inspect_framework


def materialize_snapshot_sandbox(
    source_root: str | Path,
    target_root: str | Path,
    workspace_profile: WorkspaceProfile,
    snapshot: FrameworkSnapshot,
) -> int:
    """Copy only snapshot-approved entries into a new bounded sandbox."""

    if snapshot.profile_id != workspace_profile.id:
        raise ValueError("framework snapshot does not belong to the workspace profile")

    source = Path(source_root).resolve()
    target = Path(target_root).resolve()
    if not source.is_dir():
        raise ValueError("source framework root must be an existing directory")
    if source == target or _is_within(target, source):
        raise ValueError("sandbox target must not be the source root or live inside it")
    if target.exists() and any(target.iterdir()):
        raise ValueError("sandbox target must be absent or empty")

    current = inspect_framework(
        source,
        workspace_profile,
        snapshot_id=f"{snapshot.id}_materialize_preflight",
        captured_at=datetime.now(timezone.utc),
    )
    if current.root_fingerprint != snapshot.root_fingerprint:
        raise ValueError("framework fingerprint changed before sandbox materialization")

    target.mkdir(parents=True, exist_ok=True)
    copied_files = 0
    try:
        for entry in snapshot.entries:
            destination = _safe_join(target, entry.path)
            if entry.kind is RepositoryEntryKind.DIRECTORY:
                destination.mkdir(parents=True, exist_ok=True)
                continue

            source_path = _safe_join(source, entry.path)
            if not source_path.is_file() or source_path.is_symlink():
                raise ValueError(f"snapshot source file is missing or symlinked: {entry.path}")
            data = source_path.read_bytes()
            if len(data) != entry.size_bytes:
                raise ValueError(f"snapshot source size changed: {entry.path}")
            actual_hash = hashlib.sha256(data).hexdigest()
            if actual_hash != entry.sha256:
                raise ValueError(f"snapshot source hash changed: {entry.path}")

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            copied_files += 1

        materialized = inspect_framework(
            target,
            workspace_profile,
            snapshot_id=f"{snapshot.id}_materialized",
            captured_at=datetime.now(timezone.utc),
        )
        if materialized.root_fingerprint != snapshot.root_fingerprint:
            raise ValueError("materialized sandbox does not match the approved snapshot")
    except Exception:
        shutil.rmtree(target, ignore_errors=True)
        raise

    return copied_files


def _safe_join(root: Path, relative: str) -> Path:
    candidate = root.joinpath(*relative.split("/"))
    resolved_parent = candidate.parent.resolve()
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"snapshot path escapes framework root: {relative}") from exc
    current = root
    for part in candidate.relative_to(root).parts[:-1]:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ValueError(f"symlinked snapshot parent is not supported: {relative}")
    return candidate


def _is_within(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
    except ValueError:
        return False
    return True
