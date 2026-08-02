"""Controlled representative E2E fixtures."""

import pytest


@pytest.fixture
def ecommerce_context() -> str:
    return "controlled-reference"
