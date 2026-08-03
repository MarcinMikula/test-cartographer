from pathlib import Path

import pytest

from test_cartographer.execution.io import (
    load_execution_bundle,
    load_execution_profile,
)

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def execution_profile():
    return load_execution_profile(
        ROOT / "testdata/execution/profile/strict_internal.json"
    )


@pytest.fixture
def execution_bundle():
    return load_execution_bundle(
        ROOT / "testdata/execution/bundle/reference_outcomes.json"
    )
