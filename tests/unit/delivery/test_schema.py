import json
from pathlib import Path

from test_cartographer.delivery.models import (
    CodePatch,
    CreationEvaluation,
    GenerationProfile,
    PatchApplicationReport,
)

ROOT = Path(__file__).resolve().parents[3]


def test_delivery_schemas_match_exported_files():
    cases = (
        (GenerationProfile, "generation-profile-v0.1.schema.json"),
        (CodePatch, "code-patch-v0.1.schema.json"),
        (PatchApplicationReport, "patch-application-v0.1.schema.json"),
        (CreationEvaluation, "creation-evaluation-v0.1.schema.json"),
    )
    for model, filename in cases:
        exported = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        assert exported == model.model_json_schema()
