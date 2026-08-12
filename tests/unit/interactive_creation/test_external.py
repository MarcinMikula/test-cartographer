from datetime import datetime, timezone

import pytest

from test_cartographer.context.enums import KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import ContextBundle, KnowledgeText
from test_cartographer.discovery.capture import _semantic_name, _semantic_role
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.interactive_creation.external import (
    build_external_public_single_page_plan,
)


def _provided(value: str, sensitivity=SensitivityLevel.INTERNAL) -> KnowledgeText:
    return KnowledgeText(
        value=value,
        status=KnowledgeStatus.PROVIDED,
        evidence_ids=("ev_initial_request",),
        sensitivity=sensitivity,
    )


def _context(
    outcome_text="The page presents the Driving licence codes heading.",
    *,
    source_url="https://www.gov.uk/driving-licence-codes",
):
    seed = MinimalContextSeed(
        id="seed_external",
        context_id="ctx_external",
        title="External single page",
        initial_request="Verify the page heading.",
        created_at=datetime(2026, 8, 11, 18, 0, tzinfo=timezone.utc),
        sensitivity=SensitivityLevel.PUBLIC,
    )
    context = build_minimal_context(seed)
    application = context.application.model_copy(
        update={
            "name": _provided("GOV.UK", SensitivityLevel.PUBLIC),
            "environment": _provided("public website", SensitivityLevel.PUBLIC),
            "base_url": _provided(
                source_url,
                SensitivityLevel.PUBLIC,
            ),
        }
    )
    outcome = context.process.expected_outcomes[0].model_copy(
        update={"statement": _provided(outcome_text, SensitivityLevel.PUBLIC)}
    )
    process = context.process.model_copy(
        update={
            "name": _provided("Driving licence codes", SensitivityLevel.PUBLIC),
            "expected_outcomes": (outcome,),
        }
    )
    updated = context.model_copy(update={"application": application, "process": process})
    return ContextBundle.model_validate(updated.model_dump(mode="python"))


def test_external_plan_uses_reviewed_outcome_without_locator_hint():
    plan = build_external_public_single_page_plan(
        _context(), plan_id="discovery_external"
    )

    assert plan.source_url == "https://www.gov.uk/driving-licence-codes"
    assert plan.route == "/driving-licence-codes"
    assert len(plan.targets) == 1
    assert plan.targets[0].element_id == "el_expected_heading"
    assert plan.targets[0].expected_roles == ("heading",)
    assert plan.targets[0].outcome_target is True


def test_external_plan_rejects_non_heading_scope():
    with pytest.raises(ValueError, match="heading outcomes only"):
        build_external_public_single_page_plan(
            _context("The page shows the expected information."),
            plan_id="discovery_external",
        )


def test_native_heading_has_heading_semantics():
    raw = {
        "tagName": "h1",
        "id": None,
        "role": None,
        "ariaLabel": None,
        "name": None,
        "placeholder": None,
        "type": None,
        "testId": None,
        "label": None,
        "buttonText": None,
        "headingText": "Driving licence codes",
        "disabled": False,
        "contentEditable": False,
    }

    assert _semantic_role(raw) == "heading"
    assert _semantic_name(raw) == "Driving licence codes"

@pytest.mark.parametrize(
    "source_url, message",
    (
        ("http://www.gov.uk/driving-licence-codes", "must use https"),
        ("https://localhost/example", "local hostname"),
        ("https://127.0.0.1/example", "non-global IP"),
        ("https://intranet/example", "public-style DNS hostname"),
    ),
)
def test_external_public_plan_rejects_obviously_non_public_targets(
    source_url,
    message,
):
    with pytest.raises(ValueError, match=message):
        build_external_public_single_page_plan(
            _context(source_url=source_url),
            plan_id="discovery_external",
        )
