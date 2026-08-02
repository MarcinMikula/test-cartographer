import json
from pathlib import Path

from test_cartographer.synthesis.models import (
    BoundedSynthesisRequest,
    PomProposal,
    SynthesisRun,
)

ROOT = Path(__file__).resolve().parents[3]


def test_committed_request_schema_matches_model() -> None:
    committed = json.loads(
        (ROOT / "schemas/synthesis-request-v0.1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert committed == BoundedSynthesisRequest.model_json_schema()


def test_committed_proposal_schema_matches_model() -> None:
    committed = json.loads(
        (ROOT / "schemas/pom-proposal-v0.1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert committed == PomProposal.model_json_schema()


def test_committed_run_schema_matches_model() -> None:
    committed = json.loads(
        (ROOT / "schemas/synthesis-run-v0.1.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert committed == SynthesisRun.model_json_schema()
