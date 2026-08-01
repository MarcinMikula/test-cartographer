import json
from pathlib import Path

from test_cartographer.context.models import ContextBundle

ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "schemas" / "context-bundle-v0.1.schema.json"


def test_committed_schema_matches_model() -> None:
    committed = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    assert committed == ContextBundle.model_json_schema()


def test_schema_rejects_additional_properties_at_contract_root() -> None:
    schema = ContextBundle.model_json_schema()

    assert schema["additionalProperties"] is False
    assert schema["properties"]["schema_version"]["const"] == "0.1"
