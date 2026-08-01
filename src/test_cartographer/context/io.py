"""Deterministic local JSON persistence for context contract version 0.1."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.context.models import ContextBundle


def load_context(path: str | Path) -> ContextBundle:
    """Load and strictly validate one UTF-8 JSON context bundle."""

    context_path = Path(path)
    return ContextBundle.model_validate_json(context_path.read_text(encoding="utf-8"))


def save_context(context: ContextBundle, path: str | Path) -> None:
    """Write deterministic, human-reviewable UTF-8 JSON with a trailing newline."""

    context_path = Path(path)
    context_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = context.model_dump_json(indent=2, exclude_none=False)
    context_path.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def export_json_schema(path: str | Path) -> None:
    """Export the committed JSON Schema representation of the contract."""

    schema_path = Path(path)
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        ContextBundle.model_json_schema(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    schema_path.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
