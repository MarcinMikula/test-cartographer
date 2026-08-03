"""Controlled reusable component base matching the public framework contract."""

from __future__ import annotations

from playwright.sync_api import Locator, Page


class BaseComponent:
    def __init__(self, page: Page, root: Locator | None = None) -> None:
        self.page = page
        self.root = root

    def by_test_id(self, test_id: str) -> Locator:
        if self.root is not None:
            return self.root.get_by_test_id(test_id)
        return self.page.get_by_test_id(test_id)
