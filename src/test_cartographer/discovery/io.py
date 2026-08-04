"""Deterministic JSON persistence and schemas for discovery contracts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.discovery.models import (
    DiscoveryProfile,
    ProcessDiscoveryPlan,
    ProcessDiscoveryRun,
)


def _load(path: str | Path, model):
    return model.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _save(value, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"{value.model_dump_json(indent=2, exclude_none=False)}\n",
        encoding="utf-8",
        newline="\n",
    )


def load_discovery_profile(path: str | Path) -> DiscoveryProfile:
    return _load(path, DiscoveryProfile)


def save_discovery_profile(value: DiscoveryProfile, path: str | Path) -> None:
    _save(value, path)


def load_discovery_plan(path: str | Path) -> ProcessDiscoveryPlan:
    return _load(path, ProcessDiscoveryPlan)


def save_discovery_plan(value: ProcessDiscoveryPlan, path: str | Path) -> None:
    _save(value, path)


def load_discovery_run(path: str | Path) -> ProcessDiscoveryRun:
    return _load(path, ProcessDiscoveryRun)


def save_discovery_run(value: ProcessDiscoveryRun, path: str | Path) -> None:
    _save(value, path)


def export_json_schemas(directory: str | Path) -> None:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    values = {
        "discovery-profile-v0.1.schema.json": DiscoveryProfile.model_json_schema(),
        "process-discovery-plan-v0.1.schema.json": ProcessDiscoveryPlan.model_json_schema(),
        "process-discovery-run-v0.1.schema.json": ProcessDiscoveryRun.model_json_schema(),
    }
    for name, schema in values.items():
        rendered = json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False)
        (root / name).write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
