"""Deterministic persistence for guided-intake contracts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.guided_intake.models import GuidedIntakeProfile, GuidedIntakeRun
from test_cartographer.intake.seed import MinimalContextSeed


def _load(model_type: type, path: str | Path):
    return model_type.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _save(model: object, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = model.model_dump_json(indent=2, exclude_none=False)  # type: ignore[attr-defined]
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def load_guided_profile(path: str | Path) -> GuidedIntakeProfile:
    return _load(GuidedIntakeProfile, path)


def load_guided_run(path: str | Path) -> GuidedIntakeRun:
    return _load(GuidedIntakeRun, path)


def save_guided_run(run: GuidedIntakeRun, path: str | Path) -> None:
    _save(run, path)


def load_minimal_seed(path: str | Path) -> MinimalContextSeed:
    return _load(MinimalContextSeed, path)


def export_guided_schemas(root: str | Path) -> None:
    target_root = Path(root)
    target_root.mkdir(parents=True, exist_ok=True)
    models = (
        ("minimal-context-seed-v0.1.schema.json", MinimalContextSeed),
        ("guided-intake-profile-v0.1.schema.json", GuidedIntakeProfile),
        ("guided-intake-run-v0.1.schema.json", GuidedIntakeRun),
    )
    for filename, model_type in models:
        rendered = json.dumps(
            model_type.model_json_schema(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        (target_root / filename).write_text(
            f"{rendered}\n", encoding="utf-8", newline="\n"
        )
