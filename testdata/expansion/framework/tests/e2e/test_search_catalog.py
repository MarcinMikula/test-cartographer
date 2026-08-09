import pytest

from pages.catalog_page import CatalogPage


@pytest.mark.e2e
def test_search_catalog(catalog_context) -> None:
    catalog = CatalogPage(catalog_context["page"], base_url=catalog_context["base_url"])
    catalog.open_catalog()
    catalog.search(catalog_context["query"])
    assert str(catalog_context["query"]).casefold() in catalog.read_results().casefold()
