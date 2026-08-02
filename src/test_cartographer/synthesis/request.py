"""Build and render one minimized, provider-neutral synthesis request."""

from __future__ import annotations

import json
from datetime import datetime

from test_cartographer.context.enums import KnowledgeStatus, SensitivityLevel
from test_cartographer.context.models import ContextBundle, KnowledgeText
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.synthesis.enums import ExclusionReason
from test_cartographer.synthesis.models import (
    AuthorizedAction,
    AuthorizedComponent,
    AuthorizedElement,
    AuthorizedEvidenceReference,
    AuthorizedLocator,
    AuthorizedOutcome,
    AuthorizedPage,
    AuthorizedStep,
    AuthorizedTestData,
    AuthorizedValue,
    BoundedSynthesisRequest,
    ExcludedField,
)

_ALLOWED_STATUSES = frozenset({KnowledgeStatus.CONFIRMED, KnowledgeStatus.OBSERVED})
_DEFAULT_ALLOWED_SENSITIVITY = frozenset(
    {SensitivityLevel.PUBLIC, SensitivityLevel.INTERNAL}
)

_PROHIBITED_CLAIMS = (
    "Do not claim that generated code has executed successfully.",
    "Do not claim that the proposal is business-correct without human review.",
    "Do not claim that any locator is stable beyond the supplied evidence.",
    "Do not claim that proposed objects fit an uninspected repository.",
    "Do not claim security, privacy, or compliance approval.",
    "Do not invent credential values, repository paths, or source files.",
)

_EXCLUDED_FIELDS = (
    ExcludedField(
        path="application.base_url",
        reason=ExclusionReason.POLICY,
        explanation="The POM proposal does not require an environment URL.",
    ),
    ExcludedField(
        path="pages[*].route",
        reason=ExclusionReason.POLICY,
        explanation="Routes are withheld until a repository mapping stage requires them.",
    ),
    ExcludedField(
        path="evidence[*].source_ref",
        reason=ExclusionReason.POLICY,
        explanation="Raw source references are not required for architecture synthesis.",
    ),
    ExcludedField(
        path="evidence[*].captured_at",
        reason=ExclusionReason.NOT_REQUIRED,
        explanation="Capture timestamps do not affect the first POM proposal.",
    ),
    ExcludedField(
        path="evidence[*].content_sha256",
        reason=ExclusionReason.NOT_REQUIRED,
        explanation="Content hashes remain local provenance data.",
    ),
    ExcludedField(
        path="knowledge[*].confidence",
        reason=ExclusionReason.NOT_REQUIRED,
        explanation="Only confirmed or observed values are authorized.",
    ),
    ExcludedField(
        path="knowledge[*].notes",
        reason=ExclusionReason.POLICY,
        explanation="Free-form notes are excluded from the bounded request.",
    ),
    ExcludedField(
        path="open_questions",
        reason=ExclusionReason.STATUS,
        explanation="A synthesis-ready context must not contain blocking open questions.",
    ),
    ExcludedField(
        path="conflicts",
        reason=ExclusionReason.STATUS,
        explanation="A synthesis-ready context must not contain unresolved conflicts.",
    ),
)


class RequestBuildError(ValueError):
    """Raised when context cannot be projected into an authorized request."""


def build_synthesis_request(
    context: ContextBundle,
    *,
    request_id: str,
    created_at: datetime,
    allowed_sensitivity: frozenset[SensitivityLevel] = _DEFAULT_ALLOWED_SENSITIVITY,
) -> BoundedSynthesisRequest:
    """Create a minimal request from ready, confirmed, and observed context only."""

    readiness = assess_readiness(context)
    if not readiness.ready:
        codes = ", ".join(issue.code for issue in readiness.issues)
        raise RequestBuildError(
            f"context is not ready for synthesis; unresolved readiness issues: {codes}"
        )
    if context.open_questions:
        raise RequestBuildError("synthesis context must not contain open questions")
    unresolved_conflicts = [
        conflict.id
        for conflict in context.conflicts
        if conflict.resolution.status is not KnowledgeStatus.CONFIRMED
    ]
    if unresolved_conflicts:
        raise RequestBuildError(
            f"synthesis context contains unresolved conflicts: {unresolved_conflicts}"
        )

    authorized_evidence_ids: set[str] = set()

    def value(path: str, knowledge: KnowledgeText) -> AuthorizedValue:
        if knowledge.status not in _ALLOWED_STATUSES:
            raise RequestBuildError(
                f"{path} has unauthorized status {knowledge.status.value}"
            )
        if knowledge.sensitivity not in allowed_sensitivity:
            raise RequestBuildError(
                f"{path} has disallowed sensitivity {knowledge.sensitivity.value}"
            )
        if knowledge.value is None:  # defensive; source contract already enforces this
            raise RequestBuildError(f"{path} does not contain a value")
        authorized_evidence_ids.update(knowledge.evidence_ids)
        return AuthorizedValue(
            value=knowledge.value,
            status=knowledge.status,
            evidence_ids=knowledge.evidence_ids,
            sensitivity=knowledge.sensitivity,
        )

    pages = tuple(
        AuthorizedPage(
            id=page.id,
            name=value(f"pages.{page.id}.name", page.name),
            component_ids=page.component_ids,
            element_ids=page.element_ids,
        )
        for page in context.pages
    )
    components = tuple(
        AuthorizedComponent(
            id=component.id,
            name=value(f"components.{component.id}.name", component.name),
            element_ids=component.element_ids,
        )
        for component in context.components
    )
    elements = []
    for element in context.elements:
        primary = next(
            (candidate for candidate in element.locator_candidates if candidate.primary),
            None,
        )
        if primary is None:
            raise RequestBuildError(f"element {element.id} has no primary locator")
        elements.append(
            AuthorizedElement(
                id=element.id,
                owner_id=element.owner_id,
                name=value(f"elements.{element.id}.name", element.name),
                semantic_role=value(
                    f"elements.{element.id}.semantic_role",
                    element.semantic_role,
                ),
                primary_locator=AuthorizedLocator(
                    id=primary.id,
                    strategy=primary.strategy,
                    value=value(
                        f"elements.{element.id}.locators.{primary.id}.value",
                        primary.value,
                    ),
                ),
            )
        )

    steps = tuple(
        AuthorizedStep(
            id=step.id,
            order=step.order,
            page_id=step.page_id,
            intent=value(f"steps.{step.id}.intent", step.intent),
            action=AuthorizedAction(
                kind=step.action.kind,
                target_element_id=step.action.target_element_id,
                test_data_id=step.action.test_data_id,
            ),
            expected_state=value(
                f"steps.{step.id}.expected_state",
                step.expected_state,
            ),
        )
        for step in context.process.steps
    )
    outcomes = tuple(
        AuthorizedOutcome(
            id=outcome.id,
            statement=value(
                f"outcomes.{outcome.id}.statement",
                outcome.statement,
            ),
            related_element_ids=outcome.related_element_ids,
        )
        for outcome in context.process.expected_outcomes
    )
    test_data = tuple(
        AuthorizedTestData(
            id=item.id,
            name=value(f"test_data.{item.id}.name", item.name),
            description=value(
                f"test_data.{item.id}.description",
                item.description,
            ),
            symbolic_ref=item.symbolic_ref,
            sensitivity=item.sensitivity,
        )
        for item in context.test_data
    )

    application_name = value("application.name", context.application.name)
    environment = value("application.environment", context.application.environment)
    process_name = value("process.name", context.process.name)
    purpose = value("process.purpose", context.process.purpose)
    risk = value("process.risk", context.process.risk)
    role = value("process.role", context.process.role)
    preconditions = tuple(
        value(f"process.preconditions[{index}]", item)
        for index, item in enumerate(context.process.preconditions)
    )

    evidence_by_id = {item.id: item for item in context.evidence}
    missing_evidence = sorted(authorized_evidence_ids - evidence_by_id.keys())
    if missing_evidence:
        raise RequestBuildError(
            f"authorized values reference missing evidence: {missing_evidence}"
        )
    evidence = []
    for evidence_id in sorted(authorized_evidence_ids):
        item = evidence_by_id[evidence_id]
        if item.sensitivity not in allowed_sensitivity:
            raise RequestBuildError(
                f"evidence {evidence_id} has disallowed sensitivity "
                f"{item.sensitivity.value}"
            )
        evidence.append(
            AuthorizedEvidenceReference(
                id=item.id,
                source_type=item.source_type,
                summary=item.summary,
                sensitivity=item.sensitivity,
            )
        )

    return BoundedSynthesisRequest(
        id=request_id,
        context_id=context.id,
        created_at=created_at,
        application_id=context.application.id,
        application_name=application_name,
        environment=environment,
        process_id=context.process.id,
        process_name=process_name,
        purpose=purpose,
        risk=risk,
        role=role,
        preconditions=preconditions,
        steps=steps,
        outcomes=outcomes,
        pages=pages,
        components=components,
        elements=tuple(elements),
        test_data=test_data,
        evidence=tuple(evidence),
        excluded_fields=_EXCLUDED_FIELDS,
        prohibited_claims=_PROHIBITED_CLAIMS,
    )


def render_synthesis_prompt(request: BoundedSynthesisRequest) -> str:
    """Render a deterministic provider-neutral prompt without hidden context."""

    payload = json.dumps(
        request.model_dump(mode="json"),
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )
    return (
        "Return exactly one JSON object matching POM proposal schema version 0.1.\n"
        "Do not use Markdown fences, commentary, or fields not present in the schema.\n"
        "Use only identifiers and values present in the authorized request.\n"
        "Treat every output as a proposal requiring deterministic validation and "
        "human review.\n"
        "Do not make any prohibited claim listed in the request.\n"
        "\nAUTHORIZED_SYNTHESIS_REQUEST_JSON\n"
        f"{payload}\n"
    )
