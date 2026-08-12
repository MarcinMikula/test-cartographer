"""Bounded configuration for one external public single-page Creation Flow."""

from __future__ import annotations

from ipaddress import ip_address
from urllib.parse import urlsplit

from test_cartographer.context.enums import ActionKind, SensitivityLevel
from test_cartographer.context.models import ContextBundle
from test_cartographer.discovery.models import DiscoveryTarget, ProcessDiscoveryPlan


def build_external_public_single_page_plan(
    context: ContextBundle,
    *,
    plan_id: str,
) -> ProcessDiscoveryPlan:
    """Build one heading-oriented discovery plan from reviewed intake context."""

    if len(context.pages) != 1:
        raise ValueError(
            "external public single-page creation requires exactly one context page"
        )
    if len(context.process.expected_outcomes) != 1:
        raise ValueError(
            "external public single-page creation requires exactly one expected outcome"
        )

    source_url = context.application.base_url.value
    if not source_url:
        raise ValueError("external public single-page creation requires an application URL")
    parsed = urlsplit(source_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("external public single-page URL must use https")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError(
            "external public single-page URL must not contain credentials, query, or fragment"
        )
    hostname = parsed.hostname.casefold().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
        raise ValueError("external public single-page URL must not use a local hostname")
    try:
        address = ip_address(hostname)
    except ValueError:
        if "." not in hostname:
            raise ValueError(
                "external public single-page URL must use a public-style DNS hostname"
            ) from None
    else:
        if not address.is_global:
            raise ValueError(
                "external public single-page URL must not use a non-global IP address"
            )

    outcome = context.process.expected_outcomes[0]
    outcome_text = outcome.statement.value
    if not outcome_text:
        raise ValueError("external public single-page creation requires an expected outcome")
    if "heading" not in outcome_text.casefold():
        raise ValueError(
            "external public single-page creation currently supports heading outcomes only"
        )

    page = context.pages[0]
    return ProcessDiscoveryPlan(
        id=plan_id,
        context_id=context.id,
        process_id=context.process.id,
        page_id=page.id,
        page_name=context.process.name.value or "External page",
        route=parsed.path or "/",
        source_url=source_url,
        component_ids=(),
        targets=(
            DiscoveryTarget(
                id="target_expected_heading",
                element_id="el_expected_heading",
                owner_id=page.id,
                name=outcome_text,
                action_kind=ActionKind.READ,
                expected_roles=("heading",),
                outcome_target=True,
            ),
        ),
        sensitivity=SensitivityLevel.PUBLIC,
    )
