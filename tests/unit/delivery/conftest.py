from pathlib import Path

import pytest

from test_cartographer.adaptation.io import (
    load_adaptation_plan,
    load_framework_snapshot,
    load_workspace_profile,
)
from test_cartographer.delivery.io import (
    load_application_report,
    load_code_patch,
    load_creation_evaluation,
    load_generation_profile,
)
from test_cartographer.synthesis.io import load_synthesis_run

ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture
def workspace_profile():
    return load_workspace_profile(
        ROOT / "testdata/adaptation/profile/qa_automation_framework.json"
    )


@pytest.fixture
def generation_profile():
    return load_generation_profile(
        ROOT / "testdata/delivery/profile/public_search_generation.json"
    )


@pytest.fixture
def framework_snapshot():
    return load_framework_snapshot(
        ROOT / "testdata/adaptation/snapshot/qa_automation_framework.json"
    )


@pytest.fixture
def accepted_plan():
    return load_adaptation_plan(
        ROOT / "testdata/adaptation/plan/accepted_public_search.json"
    )


@pytest.fixture
def accepted_run():
    return load_synthesis_run(
        ROOT / "testdata/synthesis/run/accepted_public_search.json"
    )


@pytest.fixture
def pending_patch():
    return load_code_patch(
        ROOT / "testdata/delivery/patch/pending_public_search.json"
    )


@pytest.fixture
def accepted_patch():
    return load_code_patch(
        ROOT / "testdata/delivery/patch/accepted_public_search.json"
    )


@pytest.fixture
def application_report():
    return load_application_report(
        ROOT / "testdata/delivery/application/applied_public_search.json"
    )


@pytest.fixture
def passed_evaluation():
    return load_creation_evaluation(
        ROOT / "testdata/delivery/evaluation/passed_public_search.json"
    )
