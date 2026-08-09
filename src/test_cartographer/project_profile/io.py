"""Deterministic local persistence and schema export for ProjectProfile v0.1."""

from __future__ import annotations

import json
from pathlib import Path

from test_cartographer.project_profile.fingerprints import validate_configuration_fingerprint
from test_cartographer.project_profile.models import ProjectProfile


def load_project_profile(path: str | Path) -> ProjectProfile:
    profile = ProjectProfile.model_validate_json(Path(path).read_text(encoding="utf-8"))
    validate_configuration_fingerprint(profile)
    return profile


def save_project_profile(profile: ProjectProfile, path: str | Path) -> None:
    validate_configuration_fingerprint(profile)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = profile.model_dump_json(indent=2, exclude_none=False)
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")


def export_project_profile_schema(path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(
        ProjectProfile.model_json_schema(),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    target.write_text(f"{rendered}\n", encoding="utf-8", newline="\n")
