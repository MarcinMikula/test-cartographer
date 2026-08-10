import pytest

from test_cartographer.validation.fingerprints import (
    compute_package_fingerprint,
    compute_run_fingerprint,
    compute_target_fingerprint,
    validate_package_fingerprint,
    validate_run_fingerprint,
    validate_target_fingerprint,
)
from test_cartographer.validation.service import create_validation_evidence_manifest


def test_target_fingerprint_is_stable(target_profile):
    assert compute_target_fingerprint(target_profile) == target_profile.target_fingerprint


def test_target_tamper_fails_closed(target_profile):
    tampered = target_profile.model_copy(update={"label": "Changed label"})
    with pytest.raises(ValueError, match="target_fingerprint mismatch"):
        validate_target_fingerprint(tampered)


def test_run_fingerprint_is_stable(validation_run):
    assert compute_run_fingerprint(validation_run) == validation_run.run_fingerprint


def test_run_tamper_fails_closed(validation_run):
    tampered = validation_run.model_copy(
        update={"target_profile_id": "different_target"}
    )
    with pytest.raises(ValueError, match="run_fingerprint mismatch"):
        validate_run_fingerprint(tampered)


def test_package_fingerprint_is_stable(target_profile, validation_run, evidence_entry):
    manifest = create_validation_evidence_manifest(
        manifest_id="validation_manifest",
        target_profile=target_profile,
        run=validation_run,
        entries=(evidence_entry,),
    )
    assert compute_package_fingerprint(manifest) == manifest.package_fingerprint


def test_package_tamper_fails_closed(
    target_profile, validation_run, evidence_entry
):
    manifest = create_validation_evidence_manifest(
        manifest_id="validation_manifest",
        target_profile=target_profile,
        run=validation_run,
        entries=(evidence_entry,),
    )
    tampered = manifest.model_copy(update={"validation_run_id": "different_run"})
    with pytest.raises(ValueError, match="package_fingerprint mismatch"):
        validate_package_fingerprint(tampered)
