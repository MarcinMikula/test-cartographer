import json
from pathlib import Path
import pytest
from test_cartographer.project_profile.io import export_project_profile_schema, load_project_profile, save_project_profile

def test_save_load_round_trip(project_profile, tmp_path):
    target = tmp_path/"project-profile.json"
    save_project_profile(project_profile, target)
    loaded = load_project_profile(target)
    assert loaded == project_profile
    assert target.read_bytes().endswith(b"\n")

def test_load_committed_fixture():
    loaded = load_project_profile("testdata/project_profile/valid/public_catalog.json")
    assert loaded.id == "project_public_catalog"
    assert loaded.revision == 1

def test_load_rejects_tampered_fingerprint(tmp_path):
    payload = json.loads(Path("testdata/project_profile/valid/public_catalog.json").read_text(encoding="utf-8"))
    payload["application"]["environment"]["value"] = "tampered"
    target = tmp_path/"tampered.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError):
        load_project_profile(target)

def test_schema_export_is_strict(tmp_path):
    target = tmp_path/"schema.json"
    export_project_profile_schema(target)
    schema = json.loads(target.read_text(encoding="utf-8"))
    assert schema["title"] == "ProjectProfile"
    assert schema["additionalProperties"] is False
