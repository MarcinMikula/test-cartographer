"""Controlled framework run producing pass, test-failure, and infrastructure evidence."""

from __future__ import annotations

import pytest

TRACEABILITY = (
    "test_search_catalog",
    "method_open_catalog",
    "method_enter_query",
    "method_submit_search",
    "assert_matching_results",
)


@pytest.fixture
def unavailable_browser_service(execution_probe):
    execution_probe.record_step(
        step_id="step_prepare_browser",
        page_object="CatalogPage",
        method_name="open_catalog",
        action="setup",
        url="https://user:password@example.test/catalog?query=Example#results",
    )
    raise RuntimeError("browser service unavailable")


def test_reference_execution_passes(execution_probe) -> None:
    execution_probe.record_step(
        step_id="step_submit_search",
        page_object="CatalogSearchForm",
        method_name="submit_search",
        action="click",
        target_element_id="el_search_submit",
        locator_id="loc_search_submit_role",
        url="https://user:password@example.test/catalog?query=Example#results",
    )
    assert True


def test_reference_test_failure_is_captured(execution_probe) -> None:
    execution_probe.record_step(
        step_id="step_assert_results",
        page_object="CatalogPage",
        method_name="read_results",
        action="assert",
        target_element_id="el_results_list",
        locator_id="loc_results_list_test_id",
        url="https://example.test/catalog?query=Example#results",
    )
    raise AssertionError("catalog result mismatch")


def test_reference_infrastructure_error_is_captured(unavailable_browser_service) -> None:
    raise AssertionError("test body must not execute")
