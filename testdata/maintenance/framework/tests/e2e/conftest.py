"""Controlled browser fixture for reactive-maintenance verification."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def catalog_context() -> Generator[dict[str, object], None, None]:
    base_url = os.environ.get("TEST_CARTOGRAPHER_CATALOG_URL")
    if not base_url:
        pytest.fail("Missing required environment variable: TEST_CARTOGRAPHER_CATALOG_URL")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(1200)
        yield {"page": page, "base_url": base_url, "search_query": "Example"}
        browser.close()
