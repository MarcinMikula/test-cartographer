"""Strict contracts for bounded LLM synthesis and POM proposal version 0.1."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import ConfigDict, Field, StringConstraints, field_validator, model_validator

from test_cartographer.context.enums import (
    ActionKind,
    EvidenceSourceType,
    KnowledgeStatus,
    LocatorStrategy,
    SensitivityLevel,
)
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.synthesis.enums import (
    ExclusionReason,
    ProposalOwnerKind,
    ProposalReviewDecision,
    SynthesisRunStatus,
    ValidationSeverity,
)

ClassName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[A-Z][A-Za-z0-9]{2,79}$"),
]
MethodName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[a-z][a-z0-9_]{2,79}$"),
]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
JsonPath = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class AuthorizedValue(ContractModel):
    """One authorized value copied into the bounded request."""

    value: NonEmptyText
    status: Literal[KnowledgeStatus.CONFIRMED, KnowledgeStatus.OBSERVED]
    evidence_ids: tuple[Identifier, ...] = Field(min_length=1)
    sensitivity: SensitivityLevel

    @field_validator("evidence_ids")
    @classmethod
    def evidence_ids_must_be_unique(
        cls,
        value: tuple[Identifier, ...],
    ) -> tuple[Identifier, ...]:
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids must be unique")
        return value


class AuthorizedLocator(ContractModel):
    id: Identifier
    strategy: LocatorStrategy
    value: AuthorizedValue


class AuthorizedElement(ContractModel):
    id: Identifier
    owner_id: Identifier
    name: AuthorizedValue
    semantic_role: AuthorizedValue
    primary_locator: AuthorizedLocator


class AuthorizedComponent(ContractModel):
    id: Identifier
    name: AuthorizedValue
    element_ids: tuple[Identifier, ...] = ()


class AuthorizedPage(ContractModel):
    id: Identifier
    name: AuthorizedValue
    component_ids: tuple[Identifier, ...] = ()
    element_ids: tuple[Identifier, ...] = ()


class AuthorizedAction(ContractModel):
    kind: ActionKind
    target_element_id: Identifier | None = None
    test_data_id: Identifier | None = None


class AuthorizedStep(ContractModel):
    id: Identifier
    order: int = Field(ge=1)
    page_id: Identifier
    intent: AuthorizedValue
    action: AuthorizedAction
    expected_state: AuthorizedValue


class AuthorizedOutcome(ContractModel):
    id: Identifier
    statement: AuthorizedValue
    related_element_ids: tuple[Identifier, ...] = ()


class AuthorizedTestData(ContractModel):
    id: Identifier
    name: AuthorizedValue
    description: AuthorizedValue
    symbolic_ref: Identifier
    sensitivity: SensitivityLevel


class AuthorizedEvidenceReference(ContractModel):
    """Minimized evidence reference; raw source content and source_ref are excluded."""

    id: Identifier
    source_type: EvidenceSourceType
    summary: NonEmptyText
    sensitivity: SensitivityLevel


class ExcludedField(ContractModel):
    path: JsonPath
    reason: ExclusionReason
    explanation: NonEmptyText


class BoundedSynthesisRequest(ContractModel):
    """Provider-neutral, minimized request for one POM proposal."""

    protocol_version: Literal["0.1"] = "0.1"
    output_schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    context_id: Identifier
    created_at: datetime
    application_id: Identifier
    application_name: AuthorizedValue
    environment: AuthorizedValue
    process_id: Identifier
    process_name: AuthorizedValue
    purpose: AuthorizedValue
    risk: AuthorizedValue
    role: AuthorizedValue
    preconditions: tuple[AuthorizedValue, ...] = Field(min_length=1)
    steps: tuple[AuthorizedStep, ...] = Field(min_length=1)
    outcomes: tuple[AuthorizedOutcome, ...] = Field(min_length=1)
    pages: tuple[AuthorizedPage, ...] = Field(min_length=1)
    components: tuple[AuthorizedComponent, ...] = ()
    elements: tuple[AuthorizedElement, ...] = Field(min_length=1)
    test_data: tuple[AuthorizedTestData, ...] = ()
    evidence: tuple[AuthorizedEvidenceReference, ...] = Field(min_length=1)
    excluded_fields: tuple[ExcludedField, ...] = ()
    prohibited_claims: tuple[NonEmptyText, ...] = Field(min_length=1)

    @field_validator("created_at")
    @classmethod
    def created_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must include a timezone offset")
        return value

    @field_validator("prohibited_claims")
    @classmethod
    def prohibited_claims_must_be_unique(
        cls,
        value: tuple[str, ...],
    ) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("prohibited_claims must be unique")
        return value

    @model_validator(mode="after")
    def validate_request_graph(self) -> BoundedSynthesisRequest:
        page_ids = {page.id for page in self.pages}
        component_ids = {component.id for component in self.components}
        element_ids = {element.id for element in self.elements}
        locator_ids = {element.primary_locator.id for element in self.elements}
        test_data_ids = {item.id for item in self.test_data}
        step_ids = {step.id for step in self.steps}
        outcome_ids = {outcome.id for outcome in self.outcomes}
        evidence_ids = {item.id for item in self.evidence}

        id_values = [
            self.id,
            self.context_id,
            self.application_id,
            self.process_id,
            *page_ids,
            *component_ids,
            *element_ids,
            *locator_ids,
            *test_data_ids,
            *step_ids,
            *outcome_ids,
            *evidence_ids,
        ]
        duplicates = sorted(
            item for item in set(id_values) if id_values.count(item) > 1
        )
        # Request ID and context IDs are allowed to be different namespaces only;
        # all actual domain IDs remain globally unique by the source contract.
        duplicates = [item for item in duplicates if item not in {self.id}]
        if duplicates:
            raise ValueError(f"authorized request ids must be globally unique: {duplicates}")

        for page in self.pages:
            unknown_components = sorted(set(page.component_ids) - component_ids)
            unknown_elements = sorted(set(page.element_ids) - element_ids)
            if unknown_components:
                raise ValueError(
                    f"page {page.id} references unknown components {unknown_components}"
                )
            if unknown_elements:
                raise ValueError(
                    f"page {page.id} references unknown elements {unknown_elements}"
                )

        for component in self.components:
            unknown_elements = sorted(set(component.element_ids) - element_ids)
            if unknown_elements:
                raise ValueError(
                    f"component {component.id} references unknown elements "
                    f"{unknown_elements}"
                )

        for element in self.elements:
            if element.owner_id not in page_ids | component_ids:
                raise ValueError(
                    f"element {element.id} references unknown owner {element.owner_id}"
                )

        for step in self.steps:
            if step.page_id not in page_ids:
                raise ValueError(
                    f"step {step.id} references unknown page {step.page_id}"
                )
            if (
                step.action.target_element_id is not None
                and step.action.target_element_id not in element_ids
            ):
                raise ValueError(
                    f"step {step.id} references unknown element "
                    f"{step.action.target_element_id}"
                )
            if (
                step.action.test_data_id is not None
                and step.action.test_data_id not in test_data_ids
            ):
                raise ValueError(
                    f"step {step.id} references unknown test data "
                    f"{step.action.test_data_id}"
                )

        for outcome in self.outcomes:
            unknown_elements = sorted(set(outcome.related_element_ids) - element_ids)
            if unknown_elements:
                raise ValueError(
                    f"outcome {outcome.id} references unknown elements "
                    f"{unknown_elements}"
                )

        referenced_evidence: set[str] = set()
        values: list[AuthorizedValue] = [
            self.application_name,
            self.environment,
            self.process_name,
            self.purpose,
            self.risk,
            self.role,
            *self.preconditions,
        ]
        for step in self.steps:
            values.extend((step.intent, step.expected_state))
        for outcome in self.outcomes:
            values.append(outcome.statement)
        for page in self.pages:
            values.append(page.name)
        for component in self.components:
            values.append(component.name)
        for element in self.elements:
            values.extend(
                (element.name, element.semantic_role, element.primary_locator.value)
            )
        for item in self.test_data:
            values.extend((item.name, item.description))
        for value in values:
            referenced_evidence.update(value.evidence_ids)
        missing_evidence = sorted(referenced_evidence - evidence_ids)
        if missing_evidence:
            raise ValueError(
                f"authorized values reference unknown evidence {missing_evidence}"
            )
        return self


class ProposedAction(ContractModel):
    step_id: Identifier
    kind: ActionKind
    target_element_id: Identifier | None = None
    locator_id: Identifier | None = None
    test_data_id: Identifier | None = None


class ProposedMethod(ContractModel):
    id: Identifier
    name: MethodName
    owner_kind: ProposalOwnerKind
    owner_source_id: Identifier
    intent: NonEmptyText
    actions: tuple[ProposedAction, ...] = Field(min_length=1)


class ProposedPageObject(ContractModel):
    id: Identifier
    class_name: ClassName
    source_page_id: Identifier
    method_ids: tuple[Identifier, ...] = ()
    component_object_ids: tuple[Identifier, ...] = ()


class ProposedComponentObject(ContractModel):
    id: Identifier
    class_name: ClassName
    source_component_id: Identifier
    method_ids: tuple[Identifier, ...] = ()


class ProposedFixture(ContractModel):
    id: Identifier
    name: MethodName
    purpose: NonEmptyText
    uses_role_from_context: bool
    uses_environment_from_context: bool
    secret_values_included: bool


class ProposedAssertion(ContractModel):
    id: Identifier
    outcome_id: Identifier
    page_id: Identifier
    related_element_ids: tuple[Identifier, ...] = ()
    intent: NonEmptyText


class ProposedTest(ContractModel):
    id: Identifier
    name: MethodName
    process_id: Identifier
    fixture_ids: tuple[Identifier, ...] = ()
    method_ids: tuple[Identifier, ...] = Field(min_length=1)
    assertions: tuple[ProposedAssertion, ...] = Field(min_length=1)


class ProposalClaimFlags(ContractModel):
    execution_success: bool = False
    business_correctness: bool = False
    locator_stability: bool = False
    repository_fit: bool = False
    security_approval: bool = False


class ProposalQuestion(ContractModel):
    id: Identifier
    question: NonEmptyText
    related_ids: tuple[Identifier, ...] = ()
    blocking: bool = False


class PomProposal(ContractModel):
    """Strict POM proposal returned by the LLM protocol."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    request_id: Identifier
    context_id: Identifier
    summary: NonEmptyText
    pages: tuple[ProposedPageObject, ...] = Field(min_length=1)
    components: tuple[ProposedComponentObject, ...] = ()
    methods: tuple[ProposedMethod, ...] = Field(min_length=1)
    fixtures: tuple[ProposedFixture, ...] = ()
    test: ProposedTest
    open_questions: tuple[ProposalQuestion, ...] = ()
    claim_flags: ProposalClaimFlags

    @model_validator(mode="after")
    def proposal_ids_must_be_unique(self) -> PomProposal:
        ids = [
            self.id,
            *(item.id for item in self.pages),
            *(item.id for item in self.components),
            *(item.id for item in self.methods),
            *(item.id for item in self.fixtures),
            self.test.id,
            *(item.id for item in self.test.assertions),
            *(item.id for item in self.open_questions),
        ]
        duplicates = sorted(item for item in set(ids) if ids.count(item) > 1)
        if duplicates:
            raise ValueError(f"proposal ids must be unique: {duplicates}")
        return self


class ProposalValidationIssue(ContractModel):
    code: Identifier
    severity: ValidationSeverity
    path: JsonPath
    message: NonEmptyText


class ProposalValidationReport(ContractModel):
    issues: tuple[ProposalValidationIssue, ...] = ()

    @property
    def valid(self) -> bool:
        return not any(
            issue.severity is ValidationSeverity.ERROR for issue in self.issues
        )

    @property
    def error_count(self) -> int:
        return sum(
            issue.severity is ValidationSeverity.ERROR for issue in self.issues
        )

    @property
    def warning_count(self) -> int:
        return sum(
            issue.severity is ValidationSeverity.WARNING for issue in self.issues
        )


class ProposalParseFailure(ContractModel):
    code: Identifier
    message: NonEmptyText


class SynthesisRun(ContractModel):
    """Exact request, raw output, parsed proposal, validation, and human review."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=False,
        validate_assignment=True,
    )

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    request: BoundedSynthesisRequest
    prompt_sha256: Sha256
    raw_output: str
    status: SynthesisRunStatus
    proposal: PomProposal | None = None
    parse_failure: ProposalParseFailure | None = None
    validation: ProposalValidationReport | None = None
    decision: ProposalReviewDecision = ProposalReviewDecision.PENDING
    started_at: datetime
    completed_at: datetime
    reviewed_at: datetime | None = None
    review_reason: NonEmptyText | None = None
    review_seconds: float = Field(default=0.0, ge=0.0)

    @field_validator("started_at", "completed_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_timezone_aware(
        cls,
        value: datetime | None,
    ) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("synthesis timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_state(self) -> SynthesisRun:
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must not be earlier than started_at")

        if self.status is SynthesisRunStatus.PROTOCOL_ERROR:
            if self.proposal is not None or self.validation is not None:
                raise ValueError("protocol_error must not contain proposal or validation")
            if self.parse_failure is None:
                raise ValueError("protocol_error requires parse_failure")
        else:
            if self.proposal is None or self.validation is None:
                raise ValueError(f"{self.status.value} requires proposal and validation")
            if self.parse_failure is not None:
                raise ValueError(f"{self.status.value} must not contain parse_failure")

        if self.status is SynthesisRunStatus.VALIDATION_REJECTED:
            if self.validation is None or self.validation.valid:
                raise ValueError("validation_rejected requires validation errors")
        if self.status in {
            SynthesisRunStatus.READY_FOR_REVIEW,
            SynthesisRunStatus.ACCEPTED,
            SynthesisRunStatus.REJECTED,
        }:
            if self.validation is None or not self.validation.valid:
                raise ValueError(f"{self.status.value} requires valid proposal validation")

        if self.status is SynthesisRunStatus.ACCEPTED:
            if self.decision is not ProposalReviewDecision.ACCEPTED:
                raise ValueError("accepted run requires accepted decision")
        elif self.status is SynthesisRunStatus.REJECTED:
            if self.decision is not ProposalReviewDecision.REJECTED:
                raise ValueError("rejected run requires rejected decision")
        elif self.decision is not ProposalReviewDecision.PENDING:
            raise ValueError("unreviewed run must keep pending decision")

        if self.decision is ProposalReviewDecision.PENDING:
            if self.reviewed_at is not None or self.review_reason is not None:
                raise ValueError("pending review must not contain review metadata")
            if self.review_seconds != 0.0:
                raise ValueError("pending review_seconds must be zero")
        else:
            if self.reviewed_at is None:
                raise ValueError("final review requires reviewed_at")
            if self.decision is ProposalReviewDecision.REJECTED and not self.review_reason:
                raise ValueError("rejected review requires a reason")
        return self
