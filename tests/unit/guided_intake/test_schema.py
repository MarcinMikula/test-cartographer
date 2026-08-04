import json
from pathlib import Path

from test_cartographer.guided_intake.models import GuidedIntakeProfile, GuidedIntakeRun
from test_cartographer.intake.seed import MinimalContextSeed

ROOT = Path(__file__).resolve().parents[3]


def test_committed_guided_schemas_match_python_contracts() -> None:
    expected = {
        "minimal-context-seed-v0.1.schema.json": MinimalContextSeed.model_json_schema(),
        "guided-intake-profile-v0.1.schema.json": GuidedIntakeProfile.model_json_schema(),
        "guided-intake-run-v0.1.schema.json": GuidedIntakeRun.model_json_schema(),
    }
    for filename, schema in expected.items():
        committed = json.loads((ROOT / "schemas" / filename).read_text(encoding="utf-8"))
        assert committed == schema
