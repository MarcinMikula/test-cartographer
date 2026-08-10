"""Canonical hashing for validation target, run, and evidence-package identities."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from test_cartographer.validation.models import (
    ValidationEvidenceManifest,
    ValidationRun,
    ValidationTargetProfile,
)


def _sha256_json(payload: object) -> str:
    rendered = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def target_identity_payload(profile: ValidationTargetProfile) -> dict[str, Any]:
    payload = profile.model_dump(mode="json", exclude_none=False)
    payload.pop("target_fingerprint", None)
    return payload


def compute_target_fingerprint(profile: ValidationTargetProfile) -> str:
    return _sha256_json(target_identity_payload(profile))


def validate_target_fingerprint(profile: ValidationTargetProfile) -> None:
    actual = compute_target_fingerprint(profile)
    if actual != profile.target_fingerprint:
        raise ValueError(
            "validation target_fingerprint mismatch: "
            f"expected {profile.target_fingerprint}, computed {actual}"
        )


def run_identity_payload(run: ValidationRun) -> dict[str, Any]:
    payload = run.model_dump(mode="json", exclude_none=False)
    payload.pop("run_fingerprint", None)
    return payload


def compute_run_fingerprint(run: ValidationRun) -> str:
    return _sha256_json(run_identity_payload(run))


def validate_run_fingerprint(run: ValidationRun) -> None:
    actual = compute_run_fingerprint(run)
    if actual != run.run_fingerprint:
        raise ValueError(
            "validation run_fingerprint mismatch: "
            f"expected {run.run_fingerprint}, computed {actual}"
        )


def package_identity_payload(
    manifest: ValidationEvidenceManifest,
) -> dict[str, Any]:
    payload = manifest.model_dump(mode="json", exclude_none=False)
    payload.pop("package_fingerprint", None)
    return payload


def compute_package_fingerprint(manifest: ValidationEvidenceManifest) -> str:
    return _sha256_json(package_identity_payload(manifest))


def validate_package_fingerprint(manifest: ValidationEvidenceManifest) -> None:
    actual = compute_package_fingerprint(manifest)
    if actual != manifest.package_fingerprint:
        raise ValueError(
            "validation package_fingerprint mismatch: "
            f"expected {manifest.package_fingerprint}, computed {actual}"
        )
