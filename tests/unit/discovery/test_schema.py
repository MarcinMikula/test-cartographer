import json
from pathlib import Path

from test_cartographer.discovery.models import DiscoveryProfile, ProcessDiscoveryPlan, ProcessDiscoveryRun

ROOT = Path(__file__).resolve().parents[3]


def test_exported_discovery_schemas_match_models() -> None:
    expected = {
        "discovery-profile-v0.1.schema.json": DiscoveryProfile.model_json_schema(),
        "process-discovery-plan-v0.1.schema.json": ProcessDiscoveryPlan.model_json_schema(),
        "process-discovery-run-v0.1.schema.json": ProcessDiscoveryRun.model_json_schema(),
    }
    for name, schema in expected.items():
        assert json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8")) == schema
