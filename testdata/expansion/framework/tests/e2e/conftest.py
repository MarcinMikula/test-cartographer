import os
from collections.abc import Generator

import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture
def catalog_context() -> Generator[dict[str, object], None, None]:
    base_url = os.environ.get("TEST_CARTOGRAPHER_CATALOG_URL")
    if not base_url:
        pytest.fail("Missing TEST_CARTOGRAPHER_CATALOG_URL")
    executable_path = os.environ.get("TEST_CARTOGRAPHER_EXECUTABLE_PATH")
    launch_args = {"headless": True}
    if executable_path:
        launch_args["executable_path"] = executable_path
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(**launch_args)
        page = browser.new_page()
        yield {
            "page": page,
            "base_url": base_url,
            "query": "Example",
            "expected_sort_order": "Alpha Beta Zulu",
        }
        browser.close()
