import json
from pathlib import Path

from test_cartographer.execution.models import (
    ExecutionEvidenceBundle,
    ExecutionEvidenceProfile,
)

ROOT = Path(__file__).resolve().parents[3]


def test_execution_schemas_match_exported_files():
    cases = (
        (ExecutionEvidenceProfile, "execution-evidence-profile-v0.1.schema.json"),
        (ExecutionEvidenceBundle, "execution-evidence-bundle-v0.1.schema.json"),
    )
    for model, filename in cases:
        exported = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        assert exported == model.model_json_schema()
