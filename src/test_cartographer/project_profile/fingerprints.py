"""Canonical hashing for ProjectProfile and referenced configuration contracts."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from test_cartographer.project_profile.models import ProjectProfile


def canonical_model_sha256(model: object) -> str:
    payload = model.model_dump(mode="json", exclude_none=False)  # type: ignore[attr-defined]
    return _sha256_json(payload)


def configuration_payload(profile: ProjectProfile) -> dict[str, Any]:
    return {
        "schema_version": profile.schema_version,
        "id": profile.id,
        "revision": profile.revision,
        "application": profile.application.model_dump(mode="json", exclude_none=False),
        "workspace_binding": profile.workspace_binding.model_dump(mode="json", exclude_none=False),
        "guided_intake_binding": profile.guided_intake_binding.model_dump(mode="json", exclude_none=False),
        "data_policy": profile.data_policy.model_dump(mode="json", exclude_none=False),
        "authentication": profile.authentication.model_dump(mode="json", exclude_none=False),
        "secret_values_persisted": profile.secret_values_persisted,
        "raw_auth_state_persisted": profile.raw_auth_state_persisted,
        "arbitrary_metadata_allowed": profile.arbitrary_metadata_allowed,
    }


def compute_configuration_fingerprint(profile: ProjectProfile) -> str:
    return _sha256_json(configuration_payload(profile))


def validate_configuration_fingerprint(profile: ProjectProfile) -> None:
    actual = compute_configuration_fingerprint(profile)
    if actual != profile.configuration_fingerprint:
        raise ValueError(
            "project profile configuration_fingerprint mismatch: "
            f"expected {profile.configuration_fingerprint}, computed {actual}"
        )


def _sha256_json(payload: object) -> str:
    rendered = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()
