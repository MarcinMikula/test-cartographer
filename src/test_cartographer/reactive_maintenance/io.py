"""JSON persistence and schema export for reactive-maintenance artefacts."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.reactive_maintenance.models import (
    MaintenanceDiagnosis,
    MaintenanceEvidenceAssessment,
    MaintenanceSourcePatch,
    ReactiveMaintenanceProfile,
    ReactiveMaintenanceRun,
)


def _load(model_type: type, path: str | Path):
    return model_type.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _save(model: object, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = model.model_dump_json(indent=2, exclude_none=False)  # type: ignore[attr-defined]
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def load_maintenance_profile(path: str | Path) -> ReactiveMaintenanceProfile:
    return _load(ReactiveMaintenanceProfile, path)


def save_maintenance_profile(model: ReactiveMaintenanceProfile, path: str | Path) -> None:
    _save(model, path)


def load_maintenance_evidence_assessment(path: str | Path) -> MaintenanceEvidenceAssessment:
    return _load(MaintenanceEvidenceAssessment, path)


def save_maintenance_evidence_assessment(model: MaintenanceEvidenceAssessment, path: str | Path) -> None:
    _save(model, path)


def load_maintenance_diagnosis(path: str | Path) -> MaintenanceDiagnosis:
    return _load(MaintenanceDiagnosis, path)


def save_maintenance_diagnosis(model: MaintenanceDiagnosis, path: str | Path) -> None:
    _save(model, path)


def load_maintenance_patch(path: str | Path) -> MaintenanceSourcePatch:
    return _load(MaintenanceSourcePatch, path)


def save_maintenance_patch(model: MaintenanceSourcePatch, path: str | Path) -> None:
    _save(model, path)


def load_maintenance_run(path: str | Path) -> ReactiveMaintenanceRun:
    return _load(ReactiveMaintenanceRun, path)


def save_maintenance_run(model: ReactiveMaintenanceRun, path: str | Path) -> None:
    _save(model, path)


def export_reactive_maintenance_schemas(directory: str | Path) -> tuple[Path, ...]:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    models = (
        (ReactiveMaintenanceProfile, "reactive-maintenance-profile-v0.1.schema.json"),
        (MaintenanceEvidenceAssessment, "maintenance-evidence-assessment-v0.1.schema.json"),
        (MaintenanceDiagnosis, "maintenance-diagnosis-v0.1.schema.json"),
        (MaintenanceSourcePatch, "maintenance-source-patch-v0.1.schema.json"),
        (ReactiveMaintenanceRun, "reactive-maintenance-run-v0.1.schema.json"),
    )
    outputs: list[Path] = []
    for model_type, name in models:
        target = root / name
        rendered = json.dumps(
            model_type.model_json_schema(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
        outputs.append(target)
    return tuple(outputs)
