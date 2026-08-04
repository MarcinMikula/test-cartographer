"""JSON persistence and schema export for creation-flow contracts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.creation_flow.models import CreationFlowProfile, CreationFlowRun


def load_creation_flow_profile(path: str | Path) -> CreationFlowProfile:
    return CreationFlowProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_creation_flow_profile(value: CreationFlowProfile, path: str | Path) -> None:
    _save(value, path)


def load_creation_flow_run(path: str | Path) -> CreationFlowRun:
    return CreationFlowRun.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_creation_flow_run(value: CreationFlowRun, path: str | Path) -> None:
    _save(value, path)


def export_json_schemas(directory: str | Path) -> None:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    values = {
        "creation-flow-profile-v0.1.schema.json": CreationFlowProfile.model_json_schema(),
        "creation-flow-run-v0.1.schema.json": CreationFlowRun.model_json_schema(),
    }
    for name, schema in values.items():
        (root / name).write_text(
            json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )


def _save(value, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        value.model_dump_json(indent=2, exclude_none=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
