"""Strict local context contract for one UI process.

Version 0.1 deliberately models one process and enough application evidence to
reason about a Page Object Model proposal. It is not an application graph and
it does not contain provider-specific or browser-runtime objects.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, ClassVar, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from test_cartographer.context.enums import (
    ActionKind,
    EvidenceSourceType,
    KnowledgeStatus,
    LocatorStrategy,
    SensitivityLevel,
)

Identifier = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        pattern=r"^[a-z][a-z0-9_]{2,63}$",
    ),
]
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ContractModel(BaseModel):
    """Shared strict configuration for every contract object."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class KnowledgeText(ContractModel):
    """A text value together with its authority, evidence, and sensitivity."""

    value: NonEmptyText | None
    status: KnowledgeStatus
    evidence_ids: tuple[Identifier, ...] = ()
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    sensitivity: SensitivityLevel = SensitivityLevel.INTERNAL
    notes: NonEmptyText | None = None

    @field_validator("evidence_ids")
    @classmethod
    def evidence_ids_must_be_unique(
        cls,
        value: tuple[Identifier, ...],
    ) -> tuple[Identifier, ...]:
        if len(value) != len(set(value)):
            raise ValueError("evidence_ids must be unique")
        return value

    @model_validator(mode="after")
    def validate_status_contract(self) -> KnowledgeText:
        if self.status is KnowledgeStatus.UNKNOWN:
            if self.value is not None:
                raise ValueError("unknown knowledge must not contain a value")
            if self.evidence_ids:
                raise ValueError("unknown knowledge must not reference evidence")
            if self.confidence is not None:
                raise ValueError("unknown knowledge must not declare confidence")
            return self

        if self.status is KnowledgeStatus.CONFLICTING:
            if self.value is not None:
                raise ValueError("conflicting knowledge must not select one value")
            if len(self.evidence_ids) < 2:
                raise ValueError(
                    "conflicting knowledge must reference at least two evidence items"
                )
            if self.confidence is not None:
                raise ValueError("conflicting knowledge must not declare confidence")
            return self

        if self.value is None:
            raise ValueError(f"{self.status.value} knowledge requires a value")
        if not self.evidence_ids:
            raise ValueError(f"{self.status.value} knowledge requires evidence")
        if self.status is KnowledgeStatus.INFERRED and self.confidence is None:
            raise ValueError("inferred knowledge requires confidence")
        return self


class Evidence(ContractModel):
    """A local provenance record; raw source content is intentionally excluded."""

    id: Identifier
    source_type: EvidenceSourceType
    source_ref: NonEmptyText
    summary: NonEmptyText
    captured_at: datetime
    sensitivity: SensitivityLevel
    content_sha256: Annotated[
        str,
        StringConstraints(pattern=r"^[0-9a-f]{64}$"),
    ] | None = None

    @field_validator("captured_at")
    @classmethod
    def captured_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone offset")
        return value


class ApplicationContext(ContractModel):
    id: Identifier
    name: KnowledgeText
    environment: KnowledgeText
    base_url: KnowledgeText


class TestDataRequirement(ContractModel):
    """Symbolic data need; no credential or business value is stored here."""

    id: Identifier
    name: KnowledgeText
    description: KnowledgeText
    symbolic_ref: Identifier
    sensitivity: SensitivityLevel


class LocatorCandidate(ContractModel):
    id: Identifier
    strategy: LocatorStrategy
    value: KnowledgeText
    primary: bool = False


class UIElement(ContractModel):
    id: Identifier
    owner_id: Identifier
    name: KnowledgeText
    semantic_role: KnowledgeText
    locator_candidates: tuple[LocatorCandidate, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def only_one_primary_locator(self) -> UIElement:
        primary_count = sum(candidate.primary for candidate in self.locator_candidates)
        if primary_count > 1:
            raise ValueError("an element may have at most one primary locator")
        return self


class ComponentContext(ContractModel):
    id: Identifier
    name: KnowledgeText
    element_ids: tuple[Identifier, ...] = ()


class PageContext(ContractModel):
    id: Identifier
    name: KnowledgeText
    route: KnowledgeText
    component_ids: tuple[Identifier, ...] = ()
    element_ids: tuple[Identifier, ...] = ()


class UIAction(ContractModel):
    kind: ActionKind
    target_element_id: Identifier | None = None
    test_data_id: Identifier | None = None

    _data_actions: ClassVar[frozenset[ActionKind]] = frozenset(
        {ActionKind.FILL, ActionKind.SELECT}
    )
    _target_only_actions: ClassVar[frozenset[ActionKind]] = frozenset(
        {
            ActionKind.CLICK,
            ActionKind.CHECK,
            ActionKind.UNCHECK,
            ActionKind.READ,
        }
    )

    @model_validator(mode="after")
    def validate_action_shape(self) -> UIAction:
        if self.kind is ActionKind.NAVIGATE:
            if self.target_element_id is not None or self.test_data_id is not None:
                raise ValueError("navigate action must not declare target or test data")
            return self

        if self.target_element_id is None:
            raise ValueError(f"{self.kind.value} action requires target_element_id")

        if self.kind in self._data_actions and self.test_data_id is None:
            raise ValueError(f"{self.kind.value} action requires test_data_id")

        if self.kind in self._target_only_actions and self.test_data_id is not None:
            raise ValueError(f"{self.kind.value} action must not declare test_data_id")

        return self


class ProcessStep(ContractModel):
    id: Identifier
    order: int = Field(ge=1)
    page_id: Identifier
    intent: KnowledgeText
    action: UIAction
    expected_state: KnowledgeText


class ExpectedOutcome(ContractModel):
    id: Identifier
    statement: KnowledgeText
    related_element_ids: tuple[Identifier, ...] = ()


class ProcessContext(ContractModel):
    id: Identifier
    name: KnowledgeText
    purpose: KnowledgeText
    risk: KnowledgeText
    role: KnowledgeText
    preconditions: tuple[KnowledgeText, ...] = Field(min_length=1)
    steps: tuple[ProcessStep, ...] = Field(min_length=1)
    expected_outcomes: tuple[ExpectedOutcome, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def step_order_must_be_contiguous(self) -> ProcessContext:
        orders = [step.order for step in self.steps]
        if orders != list(range(1, len(orders) + 1)):
            raise ValueError("process step order must be contiguous and start at 1")
        return self


class OpenQuestion(ContractModel):
    id: Identifier
    question: NonEmptyText
    related_ids: tuple[Identifier, ...]
    blocking: bool = True


class Conflict(ContractModel):
    id: Identifier
    subject_id: Identifier
    description: NonEmptyText
    evidence_ids: tuple[Identifier, ...] = Field(min_length=2)
    resolution: KnowledgeText

    @field_validator("evidence_ids")
    @classmethod
    def conflict_evidence_must_be_unique(
        cls,
        value: tuple[Identifier, ...],
    ) -> tuple[Identifier, ...]:
        if len(value) != len(set(value)):
            raise ValueError("conflict evidence_ids must be unique")
        return value


class ContextBundle(ContractModel):
    """One versioned application context bundle for one UI process."""

    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    title: NonEmptyText
    created_at: datetime
    updated_at: datetime
    application: ApplicationContext
    process: ProcessContext
    pages: tuple[PageContext, ...] = Field(min_length=1)
    components: tuple[ComponentContext, ...] = ()
    elements: tuple[UIElement, ...] = Field(min_length=1)
    test_data: tuple[TestDataRequirement, ...] = ()
    evidence: tuple[Evidence, ...] = Field(min_length=1)
    open_questions: tuple[OpenQuestion, ...] = ()
    conflicts: tuple[Conflict, ...] = ()

    @field_validator("created_at", "updated_at")
    @classmethod
    def timestamps_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("context timestamps must include a timezone offset")
        return value

    @model_validator(mode="after")
    def validate_graph_integrity(self) -> ContextBundle:
        if self.updated_at < self.created_at:
            raise ValueError("updated_at must not be earlier than created_at")

        id_groups: dict[str, tuple[str, ...]] = {
            "context": (self.id,),
            "application": (self.application.id,),
            "process": (self.process.id,),
            "pages": tuple(page.id for page in self.pages),
            "components": tuple(component.id for component in self.components),
            "elements": tuple(element.id for element in self.elements),
            "locators": tuple(
                locator.id
                for element in self.elements
                for locator in element.locator_candidates
            ),
            "test_data": tuple(item.id for item in self.test_data),
            "steps": tuple(step.id for step in self.process.steps),
            "outcomes": tuple(
                outcome.id for outcome in self.process.expected_outcomes
            ),
            "evidence": tuple(item.id for item in self.evidence),
            "questions": tuple(item.id for item in self.open_questions),
            "conflicts": tuple(item.id for item in self.conflicts),
        }
        all_ids = [item_id for ids in id_groups.values() for item_id in ids]
        duplicate_ids = sorted(
            item_id for item_id in set(all_ids) if all_ids.count(item_id) > 1
        )
        if duplicate_ids:
            raise ValueError(f"ids must be globally unique: {duplicate_ids}")

        page_ids = {page.id for page in self.pages}
        component_ids = {component.id for component in self.components}
        element_ids = {element.id for element in self.elements}
        locator_ids = {
            locator.id
            for element in self.elements
            for locator in element.locator_candidates
        }
        test_data_ids = {item.id for item in self.test_data}
        symbolic_refs = [item.symbolic_ref for item in self.test_data]
        if len(symbolic_refs) != len(set(symbolic_refs)):
            raise ValueError("test data symbolic_ref values must be unique")

        evidence_ids = {item.id for item in self.evidence}
        resolvable_ids = set(all_ids)

        self._validate_page_and_component_ownership(
            page_ids=page_ids,
            component_ids=component_ids,
            element_ids=element_ids,
        )

        page_by_id = {page.id: page for page in self.pages}
        element_by_id = {element.id: element for element in self.elements}

        for step in self.process.steps:
            if step.page_id not in page_ids:
                raise ValueError(
                    f"step {step.id} references unknown page {step.page_id}"
                )
            target_id = step.action.target_element_id
            if target_id is not None and target_id not in element_ids:
                raise ValueError(
                    f"step {step.id} references unknown element {target_id}"
                )
            if target_id is not None:
                target = element_by_id[target_id]
                page = page_by_id[step.page_id]
                target_is_direct = target.owner_id == page.id
                target_is_component = target.owner_id in page.component_ids
                if not target_is_direct and not target_is_component:
                    raise ValueError(
                        f"step {step.id} target {target_id} is not available on "
                        f"page {step.page_id}"
                    )
            data_id = step.action.test_data_id
            if data_id is not None and data_id not in test_data_ids:
                raise ValueError(
                    f"step {step.id} references unknown test data {data_id}"
                )

        for outcome in self.process.expected_outcomes:
            unknown_elements = sorted(set(outcome.related_element_ids) - element_ids)
            if unknown_elements:
                raise ValueError(
                    f"outcome {outcome.id} references unknown elements "
                    f"{unknown_elements}"
                )

        for question in self.open_questions:
            unknown_related = sorted(set(question.related_ids) - resolvable_ids)
            if unknown_related:
                raise ValueError(
                    f"question {question.id} references unknown ids {unknown_related}"
                )

        for conflict in self.conflicts:
            if conflict.subject_id not in resolvable_ids:
                raise ValueError(
                    f"conflict {conflict.id} references unknown subject "
                    f"{conflict.subject_id}"
                )
            missing = sorted(set(conflict.evidence_ids) - evidence_ids)
            if missing:
                raise ValueError(
                    f"conflict {conflict.id} references unknown evidence {missing}"
                )

        referenced_evidence = self._collect_knowledge_evidence_ids()
        missing_evidence = sorted(referenced_evidence - evidence_ids)
        if missing_evidence:
            raise ValueError(f"knowledge references unknown evidence {missing_evidence}")

        if not locator_ids:
            raise ValueError("at least one locator candidate is required")

        return self

    def _validate_page_and_component_ownership(
        self,
        *,
        page_ids: set[str],
        component_ids: set[str],
        element_ids: set[str],
    ) -> None:
        declared_element_owners: dict[str, str] = {}

        for page in self.pages:
            unknown_components = sorted(set(page.component_ids) - component_ids)
            if unknown_components:
                raise ValueError(
                    f"page {page.id} references unknown components {unknown_components}"
                )
            unknown_elements = sorted(set(page.element_ids) - element_ids)
            if unknown_elements:
                raise ValueError(
                    f"page {page.id} references unknown elements {unknown_elements}"
                )
            for element_id in page.element_ids:
                if element_id in declared_element_owners:
                    raise ValueError(
                        f"element {element_id} is declared by more than one owner"
                    )
                declared_element_owners[element_id] = page.id

        for component in self.components:
            unknown_elements = sorted(set(component.element_ids) - element_ids)
            if unknown_elements:
                raise ValueError(
                    f"component {component.id} references unknown elements "
                    f"{unknown_elements}"
                )
            for element_id in component.element_ids:
                if element_id in declared_element_owners:
                    raise ValueError(
                        f"element {element_id} is declared by more than one owner"
                    )
                declared_element_owners[element_id] = component.id

        expected_owners = page_ids | component_ids
        for element in self.elements:
            if element.owner_id not in expected_owners:
                raise ValueError(
                    f"element {element.id} references unknown owner {element.owner_id}"
                )
            if declared_element_owners.get(element.id) != element.owner_id:
                raise ValueError(
                    f"element {element.id} owner does not match page/component listing"
                )

    def _collect_knowledge_evidence_ids(self) -> set[str]:
        evidence_ids: set[str] = set()

        def add(value: KnowledgeText) -> None:
            evidence_ids.update(value.evidence_ids)

        add(self.application.name)
        add(self.application.environment)
        add(self.application.base_url)
        add(self.process.name)
        add(self.process.purpose)
        add(self.process.risk)
        add(self.process.role)

        for precondition in self.process.preconditions:
            add(precondition)
        for step in self.process.steps:
            add(step.intent)
            add(step.expected_state)
        for outcome in self.process.expected_outcomes:
            add(outcome.statement)
        for page in self.pages:
            add(page.name)
            add(page.route)
        for component in self.components:
            add(component.name)
        for element in self.elements:
            add(element.name)
            add(element.semantic_role)
            for locator in element.locator_candidates:
                add(locator.value)
        for item in self.test_data:
            add(item.name)
            add(item.description)
        for conflict in self.conflicts:
            add(conflict.resolution)

        return evidence_ids
