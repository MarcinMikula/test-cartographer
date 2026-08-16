"""Bounded configuration for one external public single-page Creation Flow."""

from __future__ import annotations

from ipaddress import ip_address
from urllib.parse import urlsplit

from test_cartographer.context.enums import ActionKind, SensitivityLevel
from test_cartographer.context.models import ContextBundle
from test_cartographer.discovery.models import DiscoveryTarget, ProcessDiscoveryPlan

_MAX_REVIEWED_TARGETS = 6
_RICH_ACTION_ROLES = {
    ActionKind.FILL: frozenset({"searchbox", "textbox"}),
    ActionKind.CLICK: frozenset({"button"}),
    ActionKind.SELECT: frozenset({"combobox"}),
    ActionKind.CHECK: frozenset({"checkbox"}),
    ActionKind.UNCHECK: frozenset({"checkbox"}),
    ActionKind.READ: frozenset({"generic", "heading", "list", "status", "table"}),
}


def external_outcome_requires_reviewed_targets(context: ContextBundle) -> bool:
    """Return whether the accepted outcome requires a rich target review."""

    if len(context.process.expected_outcomes) != 1:
        raise ValueError(
            "external public single-page creation requires exactly one expected outcome"
        )
    outcome_text = context.process.expected_outcomes[0].statement.value
    if not outcome_text:
        raise ValueError(
            "external public single-page creation requires an expected outcome"
        )
    return "heading" not in outcome_text.casefold()


def build_external_public_single_page_plan(
    context: ContextBundle,
    *,
    plan_id: str,
    reviewed_targets: tuple[DiscoveryTarget, ...] | None = None,
    component_ids: tuple[str, ...] = (),
) -> ProcessDiscoveryPlan:
    """Build one bounded plan from reviewed single-page process semantics."""

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

    page = context.pages[0]
    if reviewed_targets is None:
        if external_outcome_requires_reviewed_targets(context):
            raise ValueError(
                "external public single-page creation requires reviewed interaction "
                "targets for non-heading outcomes"
            )
        targets = (
            DiscoveryTarget(
                id="target_expected_heading",
                element_id="el_expected_heading",
                owner_id=page.id,
                name=outcome_text,
                action_kind=ActionKind.READ,
                expected_roles=("heading",),
                outcome_target=True,
            ),
        )
        declared_components: tuple[str, ...] = ()
    else:
        targets = _validate_reviewed_targets(
            reviewed_targets,
            page_id=page.id,
            component_ids=component_ids,
        )
        declared_components = component_ids

    return ProcessDiscoveryPlan(
        id=plan_id,
        context_id=context.id,
        process_id=context.process.id,
        page_id=page.id,
        page_name=context.process.name.value or "External page",
        route=parsed.path or "/",
        source_url=source_url,
        component_ids=declared_components,
        targets=targets,
        sensitivity=SensitivityLevel.PUBLIC,
    )


def _validate_reviewed_targets(
    targets: tuple[DiscoveryTarget, ...],
    *,
    page_id: str,
    component_ids: tuple[str, ...],
) -> tuple[DiscoveryTarget, ...]:
    if len(component_ids) != len(set(component_ids)):
        raise ValueError("external single-page component IDs must be unique")
    if not 2 <= len(targets) <= _MAX_REVIEWED_TARGETS:
        raise ValueError(
            "external single-page rich process requires between two and six "
            "reviewed targets"
        )
    if not any(target.action_kind is not ActionKind.READ for target in targets):
        raise ValueError(
            "external single-page rich process requires at least one interaction"
        )

    outcome_targets = [target for target in targets if target.outcome_target]
    read_targets = [
        target for target in targets if target.action_kind is ActionKind.READ
    ]
    if outcome_targets != [targets[-1]] or read_targets != [targets[-1]]:
        raise ValueError(
            "external single-page rich process requires one final READ outcome target"
        )

    owners = {page_id, *component_ids}
    symbolic_refs: list[str] = []
    for target in targets:
        if target.owner_id not in owners:
            raise ValueError(
                f"external single-page target owner is not declared: {target.owner_id}"
            )
        allowed_roles = _RICH_ACTION_ROLES.get(target.action_kind)
        if allowed_roles is None:
            raise ValueError(
                f"unsupported external single-page action: {target.action_kind.value}"
            )
        unexpected_roles = sorted(set(target.expected_roles) - allowed_roles)
        if unexpected_roles:
            raise ValueError(
                f"external single-page {target.action_kind.value} target has unsupported "
                f"roles: {unexpected_roles}"
            )
        if target.test_data_symbolic_ref is not None:
            symbolic_refs.append(target.test_data_symbolic_ref)

    if len(symbolic_refs) != len(set(symbolic_refs)):
        raise ValueError(
            "external single-page test-data symbolic references must be unique"
        )
    return targets
