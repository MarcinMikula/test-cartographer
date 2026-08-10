import json

import pytest

from test_cartographer.validation.io import (
    export_validation_schemas,
    load_validation_evidence_manifest,
    load_validation_run,
    load_validation_target_profile,
    save_validation_evidence_manifest,
    save_validation_run,
    save_validation_target_profile,
)
from test_cartographer.validation.service import create_validation_evidence_manifest


def test_target_roundtrip_is_deterministic(tmp_path, target_profile):
    path = tmp_path / "target.json"
    save_validation_target_profile(target_profile, path)
    first = path.read_bytes()
    loaded = load_validation_target_profile(path)
    save_validation_target_profile(loaded, path)
    assert path.read_bytes() == first
    assert first.endswith(b"\n")


def test_run_roundtrip_is_deterministic(tmp_path, validation_run):
    path = tmp_path / "run.json"
    save_validation_run(validation_run, path)
    first = path.read_bytes()
    loaded = load_validation_run(path)
    save_validation_run(loaded, path)
    assert path.read_bytes() == first


def test_manifest_roundtrip_is_deterministic(
    tmp_path, target_profile, validation_run, evidence_entry
):
    manifest = create_validation_evidence_manifest(
        manifest_id="validation_manifest",
        target_profile=target_profile,
        run=validation_run,
        entries=(evidence_entry,),
    )
    path = tmp_path / "manifest.json"
    save_validation_evidence_manifest(manifest, path)
    first = path.read_bytes()
    loaded = load_validation_evidence_manifest(path)
    save_validation_evidence_manifest(loaded, path)
    assert path.read_bytes() == first


def test_load_rejects_tampered_target(tmp_path, target_profile):
    path = tmp_path / "target.json"
    save_validation_target_profile(target_profile, path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["label"] = "Tampered"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="target_fingerprint mismatch"):
        load_validation_target_profile(path)


def test_schema_export_writes_four_files(tmp_path):
    export_validation_schemas(tmp_path)
    names = sorted(path.name for path in tmp_path.glob("*.schema.json"))
    assert names == [
        "validation-evidence-manifest-v0.1.schema.json",
        "validation-finding-v0.1.schema.json",
        "validation-run-v0.1.schema.json",
        "validation-target-profile-v0.1.schema.json",
    ]
