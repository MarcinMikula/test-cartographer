"""Bounded, read-only inspection of a framework workspace."""

from __future__ import annotations

import ast
import hashlib
from datetime import datetime
from pathlib import Path

from test_cartographer.adaptation.enums import PythonSymbolKind, RepositoryEntryKind
from test_cartographer.adaptation.models import (
    FrameworkSnapshot,
    PythonSymbol,
    RepositoryEntry,
    WorkspaceProfile,
)


def inspect_framework(
    framework_root: str | Path,
    profile: WorkspaceProfile,
    *,
    snapshot_id: str,
    captured_at: datetime,
) -> FrameworkSnapshot:
    root = Path(framework_root).resolve()
    if not root.is_dir():
        raise ValueError("framework_root must be an existing directory")
    for marker in profile.root_marker_files:
        if not (root / marker).is_file():
            raise ValueError(f"framework root marker is missing: {marker}")

    entries: list[RepositoryEntry] = []
    for allowed_root in profile.allowed_roots:
        candidate = root / allowed_root
        if not candidate.exists():
            continue
        if candidate.is_symlink():
            raise ValueError(f"symlinked allowed root is not supported: {allowed_root}")
        if candidate.is_file():
            entries.append(_file_entry(root, candidate, profile))
            continue
        entries.append(
            RepositoryEntry(path=allowed_root, kind=RepositoryEntryKind.DIRECTORY, size_bytes=0)
        )
        for path in sorted(candidate.rglob("*"), key=lambda item: item.as_posix()):
            if any(part in profile.ignored_names for part in path.relative_to(root).parts):
                continue
            if path.is_symlink():
                raise ValueError(f"symlinked workspace entry is not supported: {path.relative_to(root).as_posix()}")
            relative = path.relative_to(root).as_posix()
            if path.is_dir():
                entries.append(RepositoryEntry(path=relative, kind=RepositoryEntryKind.DIRECTORY, size_bytes=0))
            elif path.is_file():
                entries.append(_file_entry(root, path, profile))
            if len(entries) > profile.max_files:
                raise ValueError("workspace exceeds profile max_files")

    if not entries:
        raise ValueError("workspace inspection produced no entries")
    entries = sorted(entries, key=lambda item: (item.path, item.kind.value))
    fingerprint_payload = "\n".join(
        f"{entry.kind.value}:{entry.path}:{entry.size_bytes}:{entry.sha256 or '-'}"
        for entry in entries
    )
    fingerprint = hashlib.sha256(fingerprint_payload.encode("utf-8")).hexdigest()
    return FrameworkSnapshot(
        id=snapshot_id,
        profile_id=profile.id,
        captured_at=captured_at,
        repository_label=profile.repository_label,
        root_fingerprint=fingerprint,
        entries=tuple(entries),
    )


def _file_entry(root: Path, path: Path, profile: WorkspaceProfile) -> RepositoryEntry:
    data = path.read_bytes()
    if len(data) > profile.max_file_bytes:
        raise ValueError(f"workspace file exceeds max_file_bytes: {path.relative_to(root).as_posix()}")
    symbols: tuple[PythonSymbol, ...] = ()
    if path.suffix == ".py":
        try:
            tree = ast.parse(data.decode("utf-8"), filename=path.name)
        except (UnicodeDecodeError, SyntaxError) as exc:
            raise ValueError(f"cannot parse Python workspace file: {path.relative_to(root).as_posix()}") from exc
        symbols = tuple(_python_symbols(tree))
    return RepositoryEntry(
        path=path.relative_to(root).as_posix(),
        kind=RepositoryEntryKind.FILE,
        size_bytes=len(data),
        sha256=hashlib.sha256(data).hexdigest(),
        python_symbols=symbols,
    )


def _python_symbols(tree: ast.Module) -> list[PythonSymbol]:
    result: list[PythonSymbol] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = tuple(name for base in node.bases if (name := _node_name(base)) is not None)
            functions = [
                item for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            properties = tuple(item.name for item in functions if _is_property(item))
            methods = tuple(item.name for item in functions if not _is_property(item))
            result.append(
                PythonSymbol(
                    kind=PythonSymbolKind.CLASS,
                    name=node.name,
                    bases=bases,
                    method_names=methods,
                    property_names=properties,
                )
            )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result.append(PythonSymbol(kind=PythonSymbolKind.FUNCTION, name=node.name))
    return result


def _node_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _is_property(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(_node_name(decorator) == "property" for decorator in node.decorator_list)
