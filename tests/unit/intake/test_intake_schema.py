import json
from pathlib import Path

from test_cartographer.intake.models import IntakeSession

ROOT = Path(__file__).resolve().parents[3]


def test_committed_intake_schema_matches_python_contract() -> None:
    committed = json.loads(
        (ROOT / "schemas" / "intake-session-v0.1.schema.json").read_text(
            encoding="utf-8"
        )
    )

    assert committed == IntakeSession.model_json_schema()
    assert committed["properties"]["schema_version"]["const"] == "0.1"
