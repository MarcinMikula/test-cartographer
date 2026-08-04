import json
from pathlib import Path

from test_cartographer.creation_flow.models import CreationFlowProfile, CreationFlowRun

ROOT = Path(__file__).resolve().parents[3]


def test_creation_flow_schemas_match_exported_files() -> None:
    expected = {
        "creation-flow-profile-v0.1.schema.json": CreationFlowProfile.model_json_schema(),
        "creation-flow-run-v0.1.schema.json": CreationFlowRun.model_json_schema(),
    }
    for name, schema in expected.items():
        persisted = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        assert persisted == schema
