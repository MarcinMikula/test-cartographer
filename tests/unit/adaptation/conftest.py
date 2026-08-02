from pathlib import Path

import pytest

from test_cartographer.adaptation.io import (
    load_framework_snapshot,
    load_workspace_profile,
)
from test_cartographer.synthesis.io import load_synthesis_run


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture
def workspace_profile(repository_root):
    return load_workspace_profile(
        repository_root / "testdata/adaptation/profile/qa_automation_framework.json"
    )


@pytest.fixture
def framework_snapshot(repository_root):
    return load_framework_snapshot(
        repository_root / "testdata/adaptation/snapshot/qa_automation_framework.json"
    )


@pytest.fixture
def accepted_synthesis_run(repository_root):
    return load_synthesis_run(
        repository_root / "testdata/synthesis/run/accepted_public_search.json"
    )
