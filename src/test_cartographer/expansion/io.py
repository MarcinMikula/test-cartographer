
"""Deterministic persistence and schema export for expansion contracts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.expansion.models import (
    ExpansionAssessment,
    ExpansionPlan,
    ExpansionRequest,
    ExpansionRun,
)


def load_expansion_request(path: str | Path) -> ExpansionRequest:
    return ExpansionRequest.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_expansion_request(request: ExpansionRequest, path: str | Path) -> None:
    _save_model(request, path)


def load_expansion_plan(path: str | Path) -> ExpansionPlan:
    return ExpansionPlan.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_expansion_plan(plan: ExpansionPlan, path: str | Path) -> None:
    _save_model(plan, path)


def load_expansion_run(path: str | Path) -> ExpansionRun:
    return ExpansionRun.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_expansion_run(run: ExpansionRun, path: str | Path) -> None:
    _save_model(run, path)


def load_expansion_assessment(path: str | Path) -> ExpansionAssessment:
    return ExpansionAssessment.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_expansion_assessment(assessment: ExpansionAssessment, path: str | Path) -> None:
    _save_model(assessment, path)


def export_assessment_schema(path: str | Path) -> None:
    _export_schema(ExpansionAssessment, path)


def export_request_schema(path: str | Path) -> None:
    _export_schema(ExpansionRequest, path)


def export_plan_schema(path: str | Path) -> None:
    _export_schema(ExpansionPlan, path)


def export_run_schema(path: str | Path) -> None:
    _export_schema(ExpansionRun, path)


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
