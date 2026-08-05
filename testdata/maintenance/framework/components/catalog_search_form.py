"""Generated from accepted proposal proposal_creation_demo; review before production use."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from components.base_component import BaseComponent

TRACEABILITY = ('pom_component_search_form', 'comp_catalog_search', 'method_enter_query', 'method_submit_search')


class CatalogSearchForm(BaseComponent):
    """Application-facing actions for the mapped UI component."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    @property
    def search_query(self) -> Locator:
        """Return the observed locator loc_el_search_query_1."""
        return self.page.get_by_label('Search catalog')

    @property
    def search_submit(self) -> Locator:
        """Return the observed locator loc_el_search_submit_1."""
        return self.page.get_by_test_id('search-submit')

    def enter_query(self, value: str) -> None:
        """Enter the symbolic search query."""
        self.search_query.fill(value)

    def submit_search(self) -> None:
        """Submit the catalog search."""
        self.search_submit.click()
