"""JSON persistence and schema export for controlled source delivery."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.delivery.models import (
    CodePatch,
    CreationEvaluation,
    GenerationProfile,
    PatchApplicationReport,
)


def load_generation_profile(path: str | Path) -> GenerationProfile:
    return GenerationProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_generation_profile(profile: GenerationProfile, path: str | Path) -> None:
    _save_model(profile, path)


def load_code_patch(path: str | Path) -> CodePatch:
    return CodePatch.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_code_patch(patch: CodePatch, path: str | Path) -> None:
    _save_model(patch, path)


def load_application_report(path: str | Path) -> PatchApplicationReport:
    return PatchApplicationReport.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_application_report(report: PatchApplicationReport, path: str | Path) -> None:
    _save_model(report, path)


def load_creation_evaluation(path: str | Path) -> CreationEvaluation:
    return CreationEvaluation.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_creation_evaluation(evaluation: CreationEvaluation, path: str | Path) -> None:
    _save_model(evaluation, path)


def export_generation_profile_schema(path: str | Path) -> None:
    _export_schema(GenerationProfile, path)


def export_code_patch_schema(path: str | Path) -> None:
    _export_schema(CodePatch, path)


def export_application_report_schema(path: str | Path) -> None:
    _export_schema(PatchApplicationReport, path)


def export_creation_evaluation_schema(path: str | Path) -> None:
    _export_schema(CreationEvaluation, path)


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
