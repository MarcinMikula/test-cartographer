"""Deterministic validation of one structurally valid POM proposal."""

from __future__ import annotations

from collections import Counter

from test_cartographer.synthesis.enums import (
    ProposalOwnerKind,
    ValidationSeverity,
)
from test_cartographer.synthesis.models import (
    BoundedSynthesisRequest,
    PomProposal,
    ProposalValidationIssue,
    ProposalValidationReport,
)


def validate_pom_proposal(
    request: BoundedSynthesisRequest,
    proposal: PomProposal,
) -> ProposalValidationReport:
    """Reject unauthorized references, missing coverage, and prohibited claims."""

    issues: list[ProposalValidationIssue] = []

    def error(code: str, path: str, message: str) -> None:
        issues.append(
            ProposalValidationIssue(
                code=code,
                severity=ValidationSeverity.ERROR,
                path=path,
                message=message,
            )
        )

    def warning(code: str, path: str, message: str) -> None:
        issues.append(
            ProposalValidationIssue(
                code=code,
                severity=ValidationSeverity.WARNING,
                path=path,
                message=message,
            )
        )

    if proposal.request_id != request.id:
        error(
            "request_id_mismatch",
            "request_id",
            f"proposal request_id {proposal.request_id} does not match {request.id}",
        )
    if proposal.context_id != request.context_id:
        error(
            "context_id_mismatch",
            "context_id",
            f"proposal context_id {proposal.context_id} does not match "
            f"{request.context_id}",
        )

    request_pages = {item.id: item for item in request.pages}
    request_components = {item.id: item for item in request.components}
    request_elements = {item.id: item for item in request.elements}
    request_locators = {
        item.primary_locator.id: item.primary_locator for item in request.elements
    }
    locator_by_element = {
        item.id: item.primary_locator.id for item in request.elements
    }
    request_steps = {item.id: item for item in request.steps}
    request_test_data = {item.id: item for item in request.test_data}
    request_outcomes = {item.id: item for item in request.outcomes}

    proposed_pages = {item.id: item for item in proposal.pages}
    proposed_components = {item.id: item for item in proposal.components}
    proposed_methods = {item.id: item for item in proposal.methods}
    proposed_fixtures = {item.id: item for item in proposal.fixtures}

    page_sources = [item.source_page_id for item in proposal.pages]
    unknown_page_sources = sorted(set(page_sources) - request_pages.keys())
    if unknown_page_sources:
        error(
            "unknown_page_source",
            "pages",
            f"proposal references unauthorized pages {unknown_page_sources}",
        )
    duplicate_page_sources = sorted(
        item for item, count in Counter(page_sources).items() if count > 1
    )
    if duplicate_page_sources:
        error(
            "duplicate_page_source",
            "pages",
            f"pages are proposed more than once {duplicate_page_sources}",
        )
    missing_pages = sorted(request_pages.keys() - set(page_sources))
    if missing_pages:
        error(
            "missing_page_coverage",
            "pages",
            f"authorized pages are not represented {missing_pages}",
        )

    component_sources = [item.source_component_id for item in proposal.components]
    unknown_component_sources = sorted(
        set(component_sources) - request_components.keys()
    )
    if unknown_component_sources:
        error(
            "unknown_component_source",
            "components",
            f"proposal references unauthorized components {unknown_component_sources}",
        )
    duplicate_component_sources = sorted(
        item for item, count in Counter(component_sources).items() if count > 1
    )
    if duplicate_component_sources:
        error(
            "duplicate_component_source",
            "components",
            f"components are proposed more than once {duplicate_component_sources}",
        )
    missing_components = sorted(request_components.keys() - set(component_sources))
    if missing_components:
        error(
            "missing_component_coverage",
            "components",
            f"authorized reusable components are not represented {missing_components}",
        )

    method_reference_count: Counter[str] = Counter()
    for index, page in enumerate(proposal.pages):
        for method_id in page.method_ids:
            method_reference_count[method_id] += 1
            method = proposed_methods.get(method_id)
            if method is None:
                error(
                    "unknown_method_reference",
                    f"pages[{index}].method_ids",
                    f"page references unknown method {method_id}",
                )
            elif (
                method.owner_kind is not ProposalOwnerKind.PAGE
                or method.owner_source_id != page.source_page_id
            ):
                error(
                    "method_owner_mismatch",
                    f"pages[{index}].method_ids",
                    f"method {method_id} is not owned by page {page.source_page_id}",
                )
        expected_component_sources = set(
            request_pages.get(page.source_page_id).component_ids
            if page.source_page_id in request_pages
            else ()
        )
        actual_component_sources: set[str] = set()
        for component_id in page.component_object_ids:
            component = proposed_components.get(component_id)
            if component is None:
                error(
                    "unknown_component_object",
                    f"pages[{index}].component_object_ids",
                    f"page references unknown component object {component_id}",
                )
            else:
                actual_component_sources.add(component.source_component_id)
        if actual_component_sources != expected_component_sources:
            error(
                "page_component_mapping_mismatch",
                f"pages[{index}].component_object_ids",
                "page component mappings must exactly match authorized page components",
            )

    for index, component in enumerate(proposal.components):
        for method_id in component.method_ids:
            method_reference_count[method_id] += 1
            method = proposed_methods.get(method_id)
            if method is None:
                error(
                    "unknown_method_reference",
                    f"components[{index}].method_ids",
                    f"component references unknown method {method_id}",
                )
            elif (
                method.owner_kind is not ProposalOwnerKind.COMPONENT
                or method.owner_source_id != component.source_component_id
            ):
                error(
                    "method_owner_mismatch",
                    f"components[{index}].method_ids",
                    f"method {method_id} is not owned by component "
                    f"{component.source_component_id}",
                )

    for method_id in proposed_methods:
        count = method_reference_count[method_id]
        if count != 1:
            error(
                "method_mapping_count",
                f"methods.{method_id}",
                f"method must be mapped to exactly one owner object, found {count}",
            )

    covered_steps: list[str] = []
    for method_index, method in enumerate(proposal.methods):
        if method.owner_kind is ProposalOwnerKind.PAGE:
            if method.owner_source_id not in request_pages:
                error(
                    "unknown_method_owner",
                    f"methods[{method_index}].owner_source_id",
                    f"unknown page owner {method.owner_source_id}",
                )
        elif method.owner_source_id not in request_components:
            error(
                "unknown_method_owner",
                f"methods[{method_index}].owner_source_id",
                f"unknown component owner {method.owner_source_id}",
            )

        for action_index, action in enumerate(method.actions):
            path = f"methods[{method_index}].actions[{action_index}]"
            step = request_steps.get(action.step_id)
            if step is None:
                error(
                    "unknown_step_reference",
                    f"{path}.step_id",
                    f"unknown process step {action.step_id}",
                )
                continue
            covered_steps.append(action.step_id)
            if action.kind is not step.action.kind:
                error(
                    "action_kind_mismatch",
                    f"{path}.kind",
                    f"action kind {action.kind.value} does not match authorized "
                    f"step kind {step.action.kind.value}",
                )
            if action.target_element_id != step.action.target_element_id:
                error(
                    "target_element_mismatch",
                    f"{path}.target_element_id",
                    "target element does not match the authorized step",
                )
            if action.test_data_id != step.action.test_data_id:
                error(
                    "test_data_mismatch",
                    f"{path}.test_data_id",
                    "test data does not match the authorized step",
                )
            if action.target_element_id is None:
                if action.locator_id is not None:
                    error(
                        "unexpected_locator",
                        f"{path}.locator_id",
                        "action without a target element must not reference a locator",
                    )
            else:
                if action.target_element_id not in request_elements:
                    error(
                        "unknown_element_reference",
                        f"{path}.target_element_id",
                        f"unknown element {action.target_element_id}",
                    )
                expected_locator = locator_by_element.get(action.target_element_id)
                if action.locator_id != expected_locator:
                    error(
                        "locator_mismatch",
                        f"{path}.locator_id",
                        f"action must use authorized primary locator {expected_locator}",
                    )
                if action.locator_id not in request_locators:
                    error(
                        "unknown_locator_reference",
                        f"{path}.locator_id",
                        f"unknown locator {action.locator_id}",
                    )
            if (
                action.test_data_id is not None
                and action.test_data_id not in request_test_data
            ):
                error(
                    "unknown_test_data_reference",
                    f"{path}.test_data_id",
                    f"unknown test data {action.test_data_id}",
                )

    duplicate_steps = sorted(
        item for item, count in Counter(covered_steps).items() if count > 1
    )
    if duplicate_steps:
        error(
            "duplicate_step_coverage",
            "methods",
            f"process steps are covered more than once {duplicate_steps}",
        )
    missing_steps = sorted(request_steps.keys() - set(covered_steps))
    if missing_steps:
        error(
            "missing_step_coverage",
            "methods",
            f"process steps are not represented {missing_steps}",
        )

    if not proposal.fixtures:
        error(
            "missing_fixture_mapping",
            "fixtures",
            "proposal must represent role and environment through a symbolic fixture",
        )
    for index, fixture in enumerate(proposal.fixtures):
        if fixture.secret_values_included:
            error(
                "secret_value_claim",
                f"fixtures[{index}].secret_values_included",
                "proposal must not include secret values",
            )
        if not fixture.uses_role_from_context:
            error(
                "role_mapping_missing",
                f"fixtures[{index}].uses_role_from_context",
                "fixture must reference the authorized role concept",
            )
        if not fixture.uses_environment_from_context:
            error(
                "environment_mapping_missing",
                f"fixtures[{index}].uses_environment_from_context",
                "fixture must reference the authorized environment concept",
            )

    if proposal.test.process_id != request.process_id:
        error(
            "process_id_mismatch",
            "test.process_id",
            f"test process_id must be {request.process_id}",
        )
    unknown_fixture_ids = sorted(
        set(proposal.test.fixture_ids) - proposed_fixtures.keys()
    )
    if unknown_fixture_ids:
        error(
            "unknown_fixture_reference",
            "test.fixture_ids",
            f"test references unknown fixtures {unknown_fixture_ids}",
        )
    if set(proposal.test.fixture_ids) != proposed_fixtures.keys():
        error(
            "fixture_coverage_mismatch",
            "test.fixture_ids",
            "test must reference every proposed fixture exactly once",
        )
    unknown_test_methods = sorted(
        set(proposal.test.method_ids) - proposed_methods.keys()
    )
    if unknown_test_methods:
        error(
            "unknown_test_method",
            "test.method_ids",
            f"test references unknown methods {unknown_test_methods}",
        )
    if set(proposal.test.method_ids) != proposed_methods.keys():
        error(
            "test_method_coverage_mismatch",
            "test.method_ids",
            "test must reference every proposed method exactly once",
        )

    assertion_outcomes = [item.outcome_id for item in proposal.test.assertions]
    unknown_outcomes = sorted(set(assertion_outcomes) - request_outcomes.keys())
    if unknown_outcomes:
        error(
            "unknown_outcome_reference",
            "test.assertions",
            f"assertions reference unknown outcomes {unknown_outcomes}",
        )
    duplicate_outcomes = sorted(
        item for item, count in Counter(assertion_outcomes).items() if count > 1
    )
    if duplicate_outcomes:
        error(
            "duplicate_outcome_assertion",
            "test.assertions",
            f"outcomes are asserted more than once {duplicate_outcomes}",
        )
    missing_outcomes = sorted(request_outcomes.keys() - set(assertion_outcomes))
    if missing_outcomes:
        error(
            "missing_outcome_assertion",
            "test.assertions",
            f"authorized outcomes are not asserted {missing_outcomes}",
        )
    for index, assertion in enumerate(proposal.test.assertions):
        if assertion.page_id not in request_pages:
            error(
                "unknown_assertion_page",
                f"test.assertions[{index}].page_id",
                f"assertion references unknown page {assertion.page_id}",
            )
        outcome = request_outcomes.get(assertion.outcome_id)
        if outcome is not None and set(assertion.related_element_ids) != set(
            outcome.related_element_ids
        ):
            error(
                "assertion_element_mismatch",
                f"test.assertions[{index}].related_element_ids",
                "assertion elements must exactly match the authorized outcome",
            )

    claim_values = proposal.claim_flags.model_dump(mode="python")
    for claim_name, claimed in claim_values.items():
        if claimed:
            error(
                "prohibited_claim",
                f"claim_flags.{claim_name}",
                f"proposal makes prohibited claim: {claim_name}",
            )

    authorized_related_ids = (
        set(request_pages)
        | set(request_components)
        | set(request_elements)
        | set(request_locators)
        | set(request_steps)
        | set(request_outcomes)
        | set(request_test_data)
        | set(proposed_pages)
        | set(proposed_components)
        | set(proposed_methods)
        | set(proposed_fixtures)
        | {proposal.test.id}
    )
    for index, question in enumerate(proposal.open_questions):
        unknown_related = sorted(set(question.related_ids) - authorized_related_ids)
        if unknown_related:
            error(
                "unknown_question_reference",
                f"open_questions[{index}].related_ids",
                f"question references unknown ids {unknown_related}",
            )
        if question.blocking:
            error(
                "blocking_proposal_question",
                f"open_questions[{index}]",
                "blocking questions prevent proposal acceptance",
            )
        else:
            warning(
                "nonblocking_proposal_question",
                f"open_questions[{index}]",
                "proposal retains a non-blocking question for human review",
            )

    return ProposalValidationReport(issues=tuple(issues))
