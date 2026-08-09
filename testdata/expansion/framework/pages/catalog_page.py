from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class CatalogPage(BasePage):
    def __init__(self, page: Page, base_url: str = "") -> None:
        super().__init__(page, base_url=base_url)

    @property
    def query_input(self) -> Locator:
        return self.page.get_by_label("Search catalog")

    @property
    def search_submit(self) -> Locator:
        return self.page.get_by_test_id("search-submit")

    @property
    def results_list(self) -> Locator:
        return self.page.get_by_test_id("catalog-results")

    def open_catalog(self) -> None:
        self.open()

    def search(self, query: str) -> None:
        self.query_input.fill(query)
        self.search_submit.click()

    def read_results(self) -> str:
        return self.results_list.inner_text()
