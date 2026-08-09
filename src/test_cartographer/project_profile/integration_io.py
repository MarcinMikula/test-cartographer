"""Persistence for ProjectProfile projection/compatibility artefacts."""

from __future__ import annotations

from pathlib import Path

from test_cartographer.project_profile.integration import (
    ProjectBootstrapProjection,
    ProjectProfileCompatibilityReport,
    ProjectProfileReference,
)


def save_project_profile_reference(reference: ProjectProfileReference, path: str | Path) -> None:
    _save(reference, path)


def load_project_profile_reference(path: str | Path) -> ProjectProfileReference:
    return ProjectProfileReference.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save_project_bootstrap_projection(projection: ProjectBootstrapProjection, path: str | Path) -> None:
    _save(projection, path)


def save_project_profile_compatibility(
    report: ProjectProfileCompatibilityReport, path: str | Path
) -> None:
    _save(report, path)


def _save(model: object, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = model.model_dump_json(indent=2, exclude_none=False)  # type: ignore[attr-defined]
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
