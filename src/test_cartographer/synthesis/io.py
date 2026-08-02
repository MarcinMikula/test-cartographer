"""Deterministic JSON persistence and schema export for synthesis protocol 0.1."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.synthesis.models import (
    BoundedSynthesisRequest,
    PomProposal,
    SynthesisRun,
)


def load_synthesis_request(path: str | Path) -> BoundedSynthesisRequest:
    return BoundedSynthesisRequest.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )


def save_synthesis_request(
    request: BoundedSynthesisRequest,
    path: str | Path,
) -> None:
    _save_model(request, path)


def load_synthesis_run(path: str | Path) -> SynthesisRun:
    return SynthesisRun.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_synthesis_run(run: SynthesisRun, path: str | Path) -> None:
    _save_model(run, path)


def load_raw_output(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def export_request_schema(path: str | Path) -> None:
    _export_schema(BoundedSynthesisRequest, path)


def export_proposal_schema(path: str | Path) -> None:
    _export_schema(PomProposal, path)


def export_run_schema(path: str | Path) -> None:
    _export_schema(SynthesisRun, path)


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
