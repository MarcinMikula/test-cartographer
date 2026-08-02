from pathlib import Path

import pytest

from test_cartographer.synthesis.io import (
    load_raw_output,
    load_synthesis_request,
)
from test_cartographer.synthesis.parser import parse_pom_proposal

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def synthesis_request():
    return load_synthesis_request(
        ROOT / "testdata/synthesis/request/public_search.json"
    )


@pytest.fixture
def valid_raw_output():
    return load_raw_output(
        ROOT / "testdata/synthesis/raw/valid_public_search.json"
    )


@pytest.fixture
def valid_proposal(valid_raw_output):
    return parse_pom_proposal(valid_raw_output)
