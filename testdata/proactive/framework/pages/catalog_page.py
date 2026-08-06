from playwright.sync_api import Page


class CatalogPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

    def open(self) -> None:
        self.page.goto(self.base_url)

    def search(self, query: str) -> None:
        self.page.get_by_label("Search catalog").fill(query)
        self.page.get_by_test_id("search-submit").click()

    @property
    def results_text(self):
        return self.page.get_by_test_id("results-text")
