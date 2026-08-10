"""Deterministic persistence and schema export for validation contracts v0.1."""

from __future__ import annotations

import json
from pathlib import Path
from test_cartographer.context.models import ContractModel
from test_cartographer.validation.fingerprints import (
    validate_package_fingerprint,
    validate_run_fingerprint,
    validate_target_fingerprint,
)
from test_cartographer.validation.models import (
    ValidationEvidenceManifest,
    ValidationFinding,
    ValidationRun,
    ValidationTargetProfile,
)


def _write_model(model: ContractModel, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = model.model_dump_json(indent=2, exclude_none=False)
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def save_validation_target_profile(
    profile: ValidationTargetProfile,
    path: str | Path,
) -> None:
    validate_target_fingerprint(profile)
    _write_model(profile, path)


def load_validation_target_profile(path: str | Path) -> ValidationTargetProfile:
    profile = ValidationTargetProfile.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )
    validate_target_fingerprint(profile)
    return profile


def save_validation_run(run: ValidationRun, path: str | Path) -> None:
    validate_run_fingerprint(run)
    _write_model(run, path)


def load_validation_run(path: str | Path) -> ValidationRun:
    run = ValidationRun.model_validate_json(Path(path).read_text(encoding="utf-8"))
    validate_run_fingerprint(run)
    return run


def save_validation_evidence_manifest(
    manifest: ValidationEvidenceManifest,
    path: str | Path,
) -> None:
    validate_package_fingerprint(manifest)
    _write_model(manifest, path)


def load_validation_evidence_manifest(
    path: str | Path,
) -> ValidationEvidenceManifest:
    manifest = ValidationEvidenceManifest.model_validate_json(
        Path(path).read_text(encoding="utf-8")
    )
    validate_package_fingerprint(manifest)
    return manifest


def _export_schema(model: type[ContractModel], path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        model.model_json_schema(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def export_validation_schemas(directory: str | Path) -> None:
    root = Path(directory)
    _export_schema(
        ValidationTargetProfile,
        root / "validation-target-profile-v0.1.schema.json",
    )
    _export_schema(
        ValidationFinding,
        root / "validation-finding-v0.1.schema.json",
    )
    _export_schema(
        ValidationRun,
        root / "validation-run-v0.1.schema.json",
    )
    _export_schema(
        ValidationEvidenceManifest,
        root / "validation-evidence-manifest-v0.1.schema.json",
    )
