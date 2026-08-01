from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.context.io import load_context
from test_cartographer.observation.capture import (
    capture_page_observation,
    minimize_source_url,
    resolve_locator,
)

ROOT = Path(__file__).resolve().parents[3]
CAPTURED = datetime(2026, 8, 1, 15, 0, tzinfo=timezone.utc)


class FakeLocator:
    def __init__(
        self,
        *,
        count: int = 1,
        visible: bool = True,
        enabled: bool = True,
        editable: bool = False,
        tag_name: str = "button",
        role: str | None = None,
        content_editable: bool = False,
    ) -> None:
        self._count = count
        self._visible = visible
        self._enabled = enabled
        self._editable = editable
        self._tag_name = tag_name
        self._role = role
        self._content_editable = content_editable
        self.editable_calls = 0

    def count(self) -> int:
        return self._count

    def is_visible(self) -> bool:
        return self._visible

    def is_enabled(self) -> bool:
        return self._enabled

    def is_editable(self) -> bool:
        self.editable_calls += 1
        return self._editable

    def evaluate(self, _expression: str) -> dict[str, Any]:
        return {
            "tagName": self._tag_name,
            "id": None,
            "role": self._role,
            "ariaLabel": None,
            "name": None,
            "placeholder": None,
            "type": "submit",
            "testId": "search-submit",
            "contentEditable": self._content_editable,
            "value": "do-not-persist-this-input-value",
            "innerHTML": "<strong>Search</strong>",
            "textContent": "Search",
        }


class FakePage:
    def __init__(self, locator: FakeLocator | None = None) -> None:
        self.url = "https://catalog.example.test/catalog?token=secret#private"
        self.target = locator or FakeLocator()
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def get_by_role(self, *args: Any, **kwargs: Any) -> FakeLocator:
        self.calls.append(("role", args, kwargs))
        return self.target

    def get_by_label(self, *args: Any, **kwargs: Any) -> FakeLocator:
        self.calls.append(("label", args, kwargs))
        return self.target

    def get_by_test_id(self, *args: Any, **kwargs: Any) -> FakeLocator:
        self.calls.append(("test_id", args, kwargs))
        return self.target

    def get_by_placeholder(self, *args: Any, **kwargs: Any) -> FakeLocator:
        self.calls.append(("placeholder", args, kwargs))
        return self.target

    def get_by_text(self, *args: Any, **kwargs: Any) -> FakeLocator:
        self.calls.append(("text", args, kwargs))
        return self.target

    def locator(self, *args: Any, **kwargs: Any) -> FakeLocator:
        self.calls.append(("locator", args, kwargs))
        return self.target


def _context():
    return load_context(
        ROOT / "testdata/context/observation_ready/public_search_flow.json"
    )


def test_capture_persists_only_allowlisted_target_data() -> None:
    page = FakePage()

    observation = capture_page_observation(
        page,
        _context(),
        element_id="el_search_submit",
        observation_id="obs_search_submit",
        captured_at=CAPTURED,
        sensitivity=SensitivityLevel.PUBLIC,
        capture_seconds=0.25,
    )
    payload = observation.model_dump_json()

    assert observation.source_url == "https://catalog.example.test/catalog"
    assert observation.locator.value == "button:Search"
    assert observation.element.tag_name == "button"
    assert {item.name.value for item in observation.element.attributes} == {
        "type",
        "data-testid",
    }
    assert "do-not-persist-this-input-value" not in payload
    assert "innerHTML" not in payload
    assert "textContent" not in payload
    assert observation.element.editable is False
    assert page.target.editable_calls == 0
    assert page.calls == [("role", ("button",), {"name": "Search", "exact": True})]


def test_capture_checks_editability_only_for_supported_targets() -> None:
    locator = FakeLocator(editable=True, tag_name="input")

    observation = capture_page_observation(
        FakePage(locator),
        _context(),
        element_id="el_search_submit",
        observation_id="obs_editable_target",
        captured_at=CAPTURED,
        sensitivity=SensitivityLevel.PUBLIC,
        capture_seconds=0.1,
    )

    assert observation.element.editable is True
    assert locator.editable_calls == 1


def test_capture_rejects_ambiguous_or_invisible_target() -> None:
    for locator, message in (
        (FakeLocator(count=2), "matched 2 elements"),
        (FakeLocator(visible=False), "non-visible"),
    ):
        with pytest.raises(ValueError, match=message):
            capture_page_observation(
                FakePage(locator),
                _context(),
                element_id="el_search_submit",
                observation_id="obs_search_submit",
                captured_at=CAPTURED,
                sensitivity=SensitivityLevel.PUBLIC,
                capture_seconds=0.1,
            )


def test_minimize_source_url_removes_query_and_fragment() -> None:
    assert minimize_source_url(
        "https://example.test:8443/catalog?q=secret#token"
    ) == "https://example.test:8443/catalog"


def test_all_locator_strategies_have_deterministic_resolution() -> None:
    context = _context()
    page = FakePage()
    element = next(item for item in context.elements if item.id == "el_search_submit")
    original = element.locator_candidates[0]

    cases = [
        (LocatorStrategy.ROLE, "button:Search", "role"),
        (LocatorStrategy.LABEL, "Search", "label"),
        (LocatorStrategy.TEST_ID, "search-submit", "test_id"),
        (LocatorStrategy.PLACEHOLDER, "Search", "placeholder"),
        (LocatorStrategy.TEXT, "Search", "text"),
        (LocatorStrategy.CSS, "button[type=submit]", "locator"),
        (LocatorStrategy.XPATH, "//button", "locator"),
    ]
    for strategy, value, expected_call in cases:
        candidate = original.model_copy(
            update={
                "strategy": strategy,
                "value": original.value.model_copy(update={"value": value}),
            }
        )
        resolve_locator(page, candidate)
        assert page.calls[-1][0] == expected_call
