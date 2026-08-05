"""Generated from accepted proposal proposal_creation_demo; review before production use."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from components.catalog_search_form import CatalogSearchForm
from pages.base_page import BasePage

TRACEABILITY = ('pom_page_catalog', 'page_catalog', 'method_open_catalog', 'method_read_results', 'pom_component_search_form')


class CatalogPage(BasePage):
    """Application-facing actions and state for the mapped page."""

    def __init__(self, page: Page, base_url: str = "") -> None:
        super().__init__(page, base_url=base_url)
        self.comp_catalog_search = CatalogSearchForm(page)

    @property
    def search_results(self) -> Locator:
        """Return the observed locator loc_el_search_results_1."""
        return self.page.get_by_test_id('catalog-results')

    def open_catalog(self) -> None:
        """Open the mapped page through the framework navigation boundary."""
        self.open()

    def read_results(self) -> str:
        """Observe the matching catalog results."""
        return self.search_results.inner_text()
