"""JSON persistence and schema export for execution evidence."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.execution.models import (
    ExecutionEvidenceBundle,
    ExecutionEvidenceProfile,
)


def load_execution_profile(path: str | Path) -> ExecutionEvidenceProfile:
    return ExecutionEvidenceProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_execution_profile(profile: ExecutionEvidenceProfile, path: str | Path) -> None:
    _save_model(profile, path)


def load_execution_bundle(path: str | Path) -> ExecutionEvidenceBundle:
    return ExecutionEvidenceBundle.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_execution_bundle(bundle: ExecutionEvidenceBundle, path: str | Path) -> None:
    _save_model(bundle, path)


def export_execution_profile_schema(path: str | Path) -> None:
    _export_schema(ExecutionEvidenceProfile, path)


def export_execution_bundle_schema(path: str | Path) -> None:
    _export_schema(ExecutionEvidenceBundle, path)


def _save_model(model: object, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = model.model_dump_json(indent=2, exclude_none=False)  # type: ignore[attr-defined]
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def _export_schema(model_type: type, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        model_type.model_json_schema(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
