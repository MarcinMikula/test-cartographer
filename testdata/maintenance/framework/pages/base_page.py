"""Controlled Page Object base matching the public framework contract."""

from __future__ import annotations

from urllib.parse import urljoin
from playwright.sync_api import Locator, Page


class BasePage:
    def __init__(self, page: Page, base_url: str = "") -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def open(self, path: str = "") -> None:
        self.page.goto(self._build_url(path))

    def by_test_id(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    def _build_url(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path
        if not self.base_url:
            return path
        if not path:
            return self.base_url
        return urljoin(f"{self.base_url}/", path.lstrip("/"))
