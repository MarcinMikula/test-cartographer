from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.guided_intake.io import (
    load_guided_profile,
    load_minimal_seed,
)
from test_cartographer.intake.seed import build_minimal_context
from test_cartographer.intake.session import create_session

ROOT = Path(__file__).resolve().parents[3]
START = datetime(2026, 8, 3, 18, 0, tzinfo=timezone.utc)


@pytest.fixture
def seed():
    return load_minimal_seed(
        ROOT / "testdata" / "guided_intake" / "seed" / "product_search.json"
    )


@pytest.fixture
def replay_profile():
    return load_guided_profile(
        ROOT / "testdata" / "guided_intake" / "profile" / "replay.json"
    )


@pytest.fixture
def minimal_session(seed):
    return create_session(
        build_minimal_context(seed),
        session_id="intake_guided_reference",
        started_at=START,
    )


def render_plan(phase: str, question_ids: list[str]) -> str:
    return json.dumps(
        {
            "schema_version": "0.1",
            "phase": phase,
            "questions": [
                {
                    "question_id": question_id,
                    "user_prompt": f"Please answer {question_id}.",
                    "reason": "This closes one explicit context gap.",
                    "answer_shape": (
                        "confirmation" if phase == "review" else "sentence"
                    ),
                }
                for question_id in question_ids
            ],
        }
    )
