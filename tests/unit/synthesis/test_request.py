from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.context.enums import KnowledgeStatus, SensitivityLevel
from test_cartographer.context.io import load_context
from test_cartographer.synthesis.request import (
    RequestBuildError,
    build_synthesis_request,
    render_synthesis_prompt,
)

ROOT = Path(__file__).resolve().parents[3]


def _ready_context():
    return load_context(
        ROOT / "testdata/context/synthesis_ready/public_search_flow.json"
    )


def test_build_request_uses_only_confirmed_and_observed_context() -> None:
    request = build_synthesis_request(
        _ready_context(),
        request_id="synreq_test_build",
        created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
    )

    values = [
        request.application_name,
        request.environment,
        request.process_name,
        request.purpose,
        request.risk,
        request.role,
        *request.preconditions,
    ]
    values.extend(step.intent for step in request.steps)
    values.extend(step.expected_state for step in request.steps)
    values.extend(outcome.statement for outcome in request.outcomes)
    values.extend(page.name for page in request.pages)
    values.extend(component.name for component in request.components)
    for element in request.elements:
        values.extend(
            (element.name, element.semantic_role, element.primary_locator.value)
        )
    for item in request.test_data:
        values.extend((item.name, item.description))

    assert {item.status for item in values} <= {
        KnowledgeStatus.CONFIRMED,
        KnowledgeStatus.OBSERVED,
    }
    assert {item.sensitivity for item in values} <= {
        SensitivityLevel.PUBLIC,
        SensitivityLevel.INTERNAL,
    }


def test_request_excludes_urls_routes_and_raw_provenance() -> None:
    request = build_synthesis_request(
        _ready_context(),
        request_id="synreq_test_minimized",
        created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
    )
    rendered = request.model_dump_json()

    assert "https://catalog.example.test/" not in rendered
    assert '"/catalog"' not in rendered
    assert "tester:sprint_1_reference_definition" not in rendered
    assert "fixture:guided_catalog_observation_v1" not in rendered
    payload = request.model_dump(mode="json")
    assert all("content_sha256" not in item for item in payload["evidence"])
    assert all("source_ref" not in item for item in payload["evidence"])
    assert {item.path for item in request.excluded_fields} >= {
        "application.base_url",
        "pages[*].route",
        "evidence[*].source_ref",
    }


def test_request_preserves_symbolic_data_without_values() -> None:
    request = build_synthesis_request(
        _ready_context(),
        request_id="synreq_test_data",
        created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
    )

    assert request.test_data[0].symbolic_ref == "valid_search_query"
    assert "secret" not in request.model_dump_json().lower()


def test_request_builder_rejects_context_that_is_not_ready() -> None:
    context = load_context(
        ROOT / "testdata/context/observation_ready/public_search_flow.json"
    )

    with pytest.raises(RequestBuildError, match="not ready for synthesis"):
        build_synthesis_request(
            context,
            request_id="synreq_not_ready",
            created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
        )


def test_request_builder_rejects_unauthorized_status() -> None:
    context = _ready_context()
    supplied_name = context.application.name.model_copy(
        update={"status": KnowledgeStatus.PROVIDED}
    )
    changed = context.model_copy(
        update={
            "application": context.application.model_copy(
                update={"name": supplied_name}
            )
        }
    )

    with pytest.raises(RequestBuildError, match="unauthorized status provided"):
        build_synthesis_request(
            changed,
            request_id="synreq_bad_status",
            created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
        )


def test_request_builder_rejects_restricted_required_value() -> None:
    context = _ready_context()
    restricted_role = context.process.role.model_copy(
        update={"sensitivity": SensitivityLevel.RESTRICTED}
    )
    changed = context.model_copy(
        update={
            "process": context.process.model_copy(update={"role": restricted_role})
        }
    )

    with pytest.raises(RequestBuildError, match="disallowed sensitivity restricted"):
        build_synthesis_request(
            changed,
            request_id="synreq_restricted",
            created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
        )


def test_prompt_is_deterministic_and_contains_only_the_request() -> None:
    request = build_synthesis_request(
        _ready_context(),
        request_id="synreq_prompt",
        created_at=datetime(2026, 8, 2, 10, 0, tzinfo=timezone.utc),
    )

    first = render_synthesis_prompt(request)
    second = render_synthesis_prompt(request)

    assert first == second
    assert "AUTHORIZED_SYNTHESIS_REQUEST_JSON" in first
    assert "Return exactly one JSON object" in first
    assert "https://catalog.example.test/" not in first
    assert "/catalog" not in first
