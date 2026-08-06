import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage


@pytest.mark.e2e
def test_search_catalog(catalog_context) -> None:
    catalog = CatalogPage(
        catalog_context["page"],
        base_url=catalog_context["base_url"],
    )
    catalog.open()
    catalog.search(catalog_context["query"])
    expect(catalog.results_text).to_contain_text(catalog_context["query"])
