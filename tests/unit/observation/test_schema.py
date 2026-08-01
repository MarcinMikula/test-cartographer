import json
from pathlib import Path

from test_cartographer.observation.models import BrowserObservation

ROOT = Path(__file__).resolve().parents[3]


def test_committed_observation_schema_matches_model() -> None:
    committed = json.loads(
        (ROOT / "schemas/observation-v0.1.schema.json").read_text(encoding="utf-8")
    )

    assert committed == BrowserObservation.model_json_schema()
