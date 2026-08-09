import json
from pathlib import Path

from test_cartographer.expansion.models import (
    ExpansionAssessment,
    ExpansionPlan,
    ExpansionRequest,
    ExpansionRun,
)

ROOT = Path(__file__).resolve().parents[3]


def _committed(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def test_committed_expansion_schemas_match_models():
    expected = {
        "expansion-assessment-v0.1.schema.json": ExpansionAssessment,
        "expansion-request-v0.1.schema.json": ExpansionRequest,
        "expansion-plan-v0.1.schema.json": ExpansionPlan,
        "expansion-run-v0.1.schema.json": ExpansionRun,
    }
    for filename, model in expected.items():
        assert _committed(filename) == model.model_json_schema()
