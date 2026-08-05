import json
from pathlib import Path

from test_cartographer.interactive_creation.models import (
    ExactPatchRereviewReport,
    InteractiveCreationProfile,
    InteractiveOperatorSession,
)

ROOT = Path(__file__).resolve().parents[3]


def test_interactive_creation_schemas_match_exported_files() -> None:
    expected = {
        "interactive-creation-profile-v0.1.schema.json": InteractiveCreationProfile.model_json_schema(),
        "interactive-operator-session-v0.1.schema.json": InteractiveOperatorSession.model_json_schema(),
        "interactive-patch-rereview-v0.1.schema.json": ExactPatchRereviewReport.model_json_schema(),
    }
    for name, schema in expected.items():
        persisted = json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))
        assert persisted == schema
