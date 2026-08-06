"""Deterministic JSON I/O for proactive regression contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from test_cartographer.proactive_regression.models import (
    ObservationInventory,
    ProactiveRegressionProfile,
    ProactiveRegressionRun,
)

ModelT = TypeVar("ModelT", bound=BaseModel)


def _load(path: str | Path, model_type: type[ModelT]) -> ModelT:
    return model_type.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _save(model: BaseModel, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        model.model_dump(mode="json"),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    target.write_text(payload + "\n", encoding="utf-8", newline="\n")


def load_observation_inventory(path: str | Path) -> ObservationInventory:
    return _load(path, ObservationInventory)


def load_proactive_profile(path: str | Path) -> ProactiveRegressionProfile:
    return _load(path, ProactiveRegressionProfile)


def load_proactive_run(path: str | Path) -> ProactiveRegressionRun:
    return _load(path, ProactiveRegressionRun)


def save_proactive_run(run: ProactiveRegressionRun, path: str | Path) -> None:
    _save(run, path)
