"""Deterministic JSON persistence for browser observation version 0.1."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.observation.models import BrowserObservation


def load_observation(path: str | Path) -> BrowserObservation:
    observation_path = Path(path)
    return BrowserObservation.model_validate_json(
        observation_path.read_text(encoding="utf-8")
    )


def save_observation(observation: BrowserObservation, path: str | Path) -> None:
    observation_path = Path(path)
    observation_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = observation.model_dump_json(indent=2, exclude_none=False)
    observation_path.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def export_json_schema(path: str | Path) -> None:
    schema_path = Path(path)
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        BrowserObservation.model_json_schema(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    schema_path.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
