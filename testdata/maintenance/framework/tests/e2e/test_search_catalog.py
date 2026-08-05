"""Accepted Creation Flow test reused by reactive maintenance."""

from __future__ import annotations

import pytest

from pages.catalog_page import CatalogPage

TRACEABILITY = (
    'test_creation_catalog_search',
    'method_open_catalog',
    'method_enter_query',
    'method_submit_search',
    'method_read_results',
    'assert_creation_matching_results',
)


@pytest.mark.e2e
@pytest.mark.cartographer(
    context_id="ctx_cb1897ffad97",
    process_id="proc_target",
    synthesis_run_id="synrun_210caae45058",
    adaptation_plan_id="adapt_a60379078f5b",
    code_patch_id="patch_rereview_7c2de0c8e20e",
)
def test_search_catalog(catalog_context, execution_probe) -> None:
    page = catalog_context["page"]
    catalog_page = CatalogPage(page, base_url=catalog_context["base_url"])
    execution_probe.record_step(step_id="step_open_catalog", page_object="CatalogPage", method_name="open_catalog", action="navigate", url=str(catalog_context["base_url"]))
    catalog_page.open_catalog()
    execution_probe.record_step(step_id="step_enter_query", page_object="CatalogSearchForm", method_name="enter_query", action="fill", target_element_id="el_search_query", locator_id="loc_el_search_query_1", url=page.url)
    catalog_page.comp_catalog_search.enter_query(catalog_context["search_query"])
    execution_probe.record_step(step_id="step_submit_search", page_object="CatalogSearchForm", method_name="submit_search", action="click", target_element_id="el_search_submit", locator_id="loc_el_search_submit_1", url=page.url)
    catalog_page.comp_catalog_search.submit_search()
    execution_probe.record_step(step_id="step_read_results", page_object="CatalogPage", method_name="read_results", action="read", target_element_id="el_search_results", locator_id="loc_el_search_results_1", url=page.url)
    read_results_value = catalog_page.read_results()
    expected_fragment = str(catalog_context["search_query"]).casefold()
    assert expected_fragment in str(read_results_value).casefold(), "The visible results do not contain the explicitly supplied search query."
