"""Deterministic JSON persistence and schema export for adaptation contracts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.adaptation.models import (
    AdaptationPlan,
    FrameworkSnapshot,
    WorkspaceProfile,
)


def load_workspace_profile(path: str | Path) -> WorkspaceProfile:
    return WorkspaceProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_workspace_profile(profile: WorkspaceProfile, path: str | Path) -> None:
    _save_model(profile, path)


def load_framework_snapshot(path: str | Path) -> FrameworkSnapshot:
    return FrameworkSnapshot.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )


def save_framework_snapshot(snapshot: FrameworkSnapshot, path: str | Path) -> None:
    _save_model(snapshot, path)


def load_adaptation_plan(path: str | Path) -> AdaptationPlan:
    return AdaptationPlan.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_adaptation_plan(plan: AdaptationPlan, path: str | Path) -> None:
    _save_model(plan, path)


def export_profile_schema(path: str | Path) -> None:
    _export_schema(WorkspaceProfile, path)


def export_snapshot_schema(path: str | Path) -> None:
    _export_schema(FrameworkSnapshot, path)


def export_plan_schema(path: str | Path) -> None:
    _export_schema(AdaptationPlan, path)


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
