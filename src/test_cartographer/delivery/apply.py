"""Preflighted and rollback-capable application of an accepted code patch."""

from __future__ import annotations

import hashlib
import os
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.models import FrameworkSnapshot, WorkspaceProfile
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.delivery.enums import CodePatchStatus, SourceChangeKind
from test_cartographer.delivery.models import (
    AppliedChange,
    CodePatch,
    PatchApplicationReport,
)

TimerFn = Callable[[], float]


def apply_code_patch(
    patch: CodePatch,
    workspace_profile: WorkspaceProfile,
    snapshot: FrameworkSnapshot,
    framework_root: str | Path,
    *,
    application_id: str,
    applied_at: datetime,
    timer_fn: TimerFn = time.perf_counter,
) -> PatchApplicationReport:
    """Apply an accepted patch after a complete no-write preflight."""

    if patch.status is not CodePatchStatus.ACCEPTED:
        raise ValueError("only a human-accepted code patch can be applied")
    if patch.workspace_profile_id != workspace_profile.id:
        raise ValueError("code patch does not belong to the workspace profile")
    if patch.snapshot_id != snapshot.id or patch.snapshot_fingerprint != snapshot.root_fingerprint:
        raise ValueError("code patch does not match the supplied framework snapshot")
    if snapshot.profile_id != workspace_profile.id:
        raise ValueError("framework snapshot does not belong to the workspace profile")

    root = Path(framework_root).resolve()
    current = inspect_framework(
        root,
        workspace_profile,
        snapshot_id=f"{snapshot.id}_apply_preflight",
        captured_at=datetime.now(timezone.utc),
    )
    if current.root_fingerprint != snapshot.root_fingerprint:
        raise ValueError("framework fingerprint changed before patch application")

    allowed_roots = tuple(workspace_profile.allowed_roots)
    planned: list[tuple[Path, bytes | None, bytes, str | None]] = []
    for change in patch.changes:
        if not _path_is_allowed(change.target_path, allowed_roots):
            raise ValueError(f"patch target is outside workspace allowlist: {change.target_path}")
        target = _safe_target(root, change.target_path)
        if change.kind is SourceChangeKind.CREATE_FILE:
            if target.exists():
                raise ValueError(f"create_file target already exists: {change.target_path}")
            before_bytes = None
            before_hash = None
            after_bytes = change.content.encode("utf-8")
        else:
            if not target.is_file():
                raise ValueError(f"existing-file change target is missing: {change.target_path}")
            before_bytes = target.read_bytes()
            before_hash = hashlib.sha256(before_bytes).hexdigest()
            if before_hash != change.expected_before_sha256:
                raise ValueError(f"existing-file target hash changed: {change.target_path}")
            if change.kind is SourceChangeKind.APPEND_SYMBOL:
                after_bytes = before_bytes + change.content.encode("utf-8")
            elif change.kind is SourceChangeKind.REPLACE_FILE:
                after_bytes = change.content.encode("utf-8")
            else:
                raise ValueError(f"unsupported source change kind: {change.kind.value}")
        actual_after = hashlib.sha256(after_bytes).hexdigest()
        if actual_after != change.expected_after_sha256:
            raise ValueError(f"planned after hash does not match rendered content: {change.target_path}")
        planned.append((target, before_bytes, after_bytes, before_hash))

    started = timer_fn()
    written: list[tuple[Path, bytes | None]] = []
    try:
        for target, before_bytes, after_bytes, _ in planned:
            target.parent.mkdir(parents=True, exist_ok=True)
            _assert_no_symlink_between(root, target.parent)
            temporary = target.with_name(f".{target.name}.test-cartographer.tmp")
            temporary.write_bytes(after_bytes)
            os.replace(temporary, target)
            written.append((target, before_bytes))
    except Exception:
        for target, before_bytes in reversed(written):
            if before_bytes is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(before_bytes)
        raise
    elapsed = max(0.0, timer_fn() - started)

    after = inspect_framework(
        root,
        workspace_profile,
        snapshot_id=f"{snapshot.id}_after_apply",
        captured_at=datetime.now(timezone.utc),
    )
    applied_changes = tuple(
        AppliedChange(
            operation_id=change.operation_id,
            target_path=change.target_path,
            before_sha256=before_hash,
            after_sha256=change.expected_after_sha256,
            bytes_written=len(after_bytes),
        )
        for change, (_, _, after_bytes, before_hash) in zip(patch.changes, planned, strict=True)
    )
    return PatchApplicationReport(
        id=application_id,
        patch_id=patch.id,
        plan_id=patch.plan_id,
        snapshot_id=patch.snapshot_id,
        snapshot_fingerprint=patch.snapshot_fingerprint,
        applied_at=applied_at,
        application_seconds=elapsed,
        changes=applied_changes,
        after_fingerprint=after.root_fingerprint,
    )


def _path_is_allowed(path: str, allowed_roots: tuple[str, ...]) -> bool:
    return any(path == root or path.startswith(f"{root}/") for root in allowed_roots)


def _safe_target(root: Path, relative: str) -> Path:
    target = root.joinpath(*relative.split("/"))
    if target.is_symlink():
        raise ValueError(f"symlinked patch target is not supported: {relative}")
    resolved_parent = target.parent.resolve()
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"patch target escapes framework root: {relative}") from exc
    _assert_no_symlink_between(root, target.parent)
    return target


def _assert_no_symlink_between(root: Path, directory: Path) -> None:
    current = root
    for part in directory.relative_to(root).parts:
        current = current / part
        if current.exists() and current.is_symlink():
            raise ValueError(f"symlinked patch parent is not supported: {current.relative_to(root)}")
