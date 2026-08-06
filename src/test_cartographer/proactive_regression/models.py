"""Strict contracts for one bounded proactive regression run."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import Field, StringConstraints, field_validator, model_validator

from test_cartographer.context.enums import LocatorStrategy, SensitivityLevel
from test_cartographer.context.models import ContractModel, Identifier, NonEmptyText
from test_cartographer.proactive_regression.enums import (
    AuthenticationMode,
    AutomationImpact,
    ChangeDisposition,
    InventoryReviewDecision,
    ProactiveRunStatus,
    ReportReviewDecision,
)

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
RelativePath = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[A-Za-z0-9_.\-/]+$"),
]
EnvironmentVariableName = Annotated[
    str,
    StringConstraints(strip_whitespace=True, pattern=r"^[A-Z][A-Z0-9_]{2,63}$"),
]


def _require_aware(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must include a timezone offset")
    return value


def _validate_relative_path(value: str) -> str:
    candidate = value.replace("\\", "/")
    if candidate.startswith("/") or ".." in candidate.split("/"):
        raise ValueError("path must be relative and must not traverse parent directories")
    return candidate


def _validate_origin(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("origin must use http or https and include a host")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("origin must not contain credentials, query, or fragment")
    if parsed.path not in {"", "/"}:
        raise ValueError("origin must not contain an application path")
    return f"{parsed.scheme}://{parsed.netloc}"


class ObservationBudget(ContractModel):
    max_pages: int = Field(ge=1, le=5)
    max_elements: int = Field(ge=1, le=50)
    navigation_timeout_ms: int = Field(ge=100, le=60_000)
    locator_timeout_ms: int = Field(ge=100, le=10_000)


class ApprovedObservationItem(ContractModel):
    id: Identifier
    page_id: Identifier
    element_id: Identifier
    route: NonEmptyText
    semantic_role: NonEmptyText
    accessible_name: NonEmptyText
    primary_locator_strategy: LocatorStrategy
    primary_locator_value: NonEmptyText
    covered_by_current_framework_test: bool

    @field_validator("route")
    @classmethod
    def route_is_application_relative(cls, value: str) -> str:
        if not value.startswith("/") or value.startswith("//"):
            raise ValueError("route must be one application-relative path")
        if "?" in value or "#" in value:
            raise ValueError("route must not contain query or fragment")
        return value


class ObservationInventory(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    context_bundle_id: Identifier
    process_id: Identifier
    base_origin: NonEmptyText
    allowed_routes: tuple[NonEmptyText, ...] = Field(min_length=1, max_length=5)
    allowed_actions: tuple[Literal["navigate", "observe"], ...] = Field(
        min_length=2, max_length=2
    )
    authentication_mode: AuthenticationMode
    sensitivity: SensitivityLevel
    budget: ObservationBudget
    review_decision: InventoryReviewDecision
    human_approved: bool
    accepted_at: datetime
    items: tuple[ApprovedObservationItem, ...] = Field(min_length=1)

    @field_validator("base_origin")
    @classmethod
    def base_origin_is_bounded(cls, value: str) -> str:
        return _validate_origin(value)

    @field_validator("accepted_at")
    @classmethod
    def accepted_at_is_aware(cls, value: datetime) -> datetime:
        return _require_aware(value, "accepted_at")

    @field_validator("allowed_actions")
    @classmethod
    def allowed_actions_are_exact(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if set(value) != {"navigate", "observe"}:
            raise ValueError("allowed_actions must contain navigate and observe exactly once")
        return value

    @field_validator("allowed_routes")
    @classmethod
    def allowed_routes_are_unique(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("allowed_routes must be unique")
        for route in value:
            if not route.startswith("/") or route.startswith("//"):
                raise ValueError("every allowed route must be application-relative")
            if "?" in route or "#" in route:
                raise ValueError("allowed routes must not contain query or fragment")
        return value

    @model_validator(mode="after")
    def validate_inventory_boundary(self) -> "ObservationInventory":
        if self.authentication_mode is not AuthenticationMode.NONE:
            raise ValueError("Sprint 13 supports public no-auth observation only")
        if self.sensitivity is not SensitivityLevel.PUBLIC:
            raise ValueError("Sprint 13 inventory must be PUBLIC")
        if self.review_decision is not InventoryReviewDecision.ACCEPTED:
            raise ValueError("inventory must be human accepted before execution")
        if not self.human_approved:
            raise ValueError("inventory must preserve explicit human approval")
        if len(self.items) > self.budget.max_elements:
            raise ValueError("inventory exceeds max_elements budget")
        page_ids = {item.page_id for item in self.items}
        if len(page_ids) > self.budget.max_pages:
            raise ValueError("inventory exceeds max_pages budget")
        if len({item.id for item in self.items}) != len(self.items):
            raise ValueError("inventory item IDs must be unique")
        if len({item.element_id for item in self.items}) != len(self.items):
            raise ValueError("inventory element IDs must be unique")
        allowed = set(self.allowed_routes)
        unknown_routes = sorted({item.route for item in self.items} - allowed)
        if unknown_routes:
            raise ValueError(f"inventory item routes are not allowlisted: {unknown_routes}")
        return self


class ProactiveRegressionProfile(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    inventory_id: Identifier
    allowed_origin: NonEmptyText
    baseline_document: RelativePath
    current_document: RelativePath
    framework_test_path: RelativePath
    framework_url_environment_variable: EnvironmentVariableName
    framework_probe_timeout_seconds: float = Field(ge=1.0, le=120.0)
    require_headed_browser_for_real_operator: bool = True
    max_operator_actions: Literal[3] = 3
    expected_stable_count: int = Field(ge=1, le=50)
    expected_drift_count: int = Field(ge=1, le=50)
    persist_raw_page: Literal[False] = False
    persist_html: Literal[False] = False
    persist_screenshot: Literal[False] = False
    allow_automatic_patch: Literal[False] = False
    allow_context_write: Literal[False] = False
    live_llm_enabled: Literal[False] = False

    @field_validator("allowed_origin")
    @classmethod
    def allowed_origin_is_bounded(cls, value: str) -> str:
        return _validate_origin(value)

    @field_validator("baseline_document", "current_document", "framework_test_path")
    @classmethod
    def paths_are_relative(cls, value: str) -> str:
        return _validate_relative_path(value)

    @model_validator(mode="after")
    def documents_must_differ(self) -> "ProactiveRegressionProfile":
        if self.baseline_document == self.current_document:
            raise ValueError("baseline_document and current_document must differ")
        return self


class ObservedAttribute(ContractModel):
    name: Literal["data-testid", "id", "name", "type", "aria-label"]
    value: NonEmptyText


class ElementRegressionObservation(ContractModel):
    item_id: Identifier
    element_id: Identifier
    disposition: ChangeDisposition
    automation_impact: AutomationImpact
    covered_by_current_framework_test: bool
    expected_locator_strategy: LocatorStrategy
    expected_locator_value: NonEmptyText
    expected_locator_visible_count: int = Field(ge=0, le=50)
    semantic_visible_count: int = Field(ge=0, le=50)
    current_locator_strategy: LocatorStrategy | None = None
    current_locator_value: NonEmptyText | None = None
    observed_attributes: tuple[ObservedAttribute, ...] = ()
    observation_sha256: Sha256

    @model_validator(mode="after")
    def validate_disposition_shape(self) -> "ElementRegressionObservation":
        has_current = (
            self.current_locator_strategy is not None
            and self.current_locator_value is not None
        )
        if (self.current_locator_strategy is None) != (self.current_locator_value is None):
            raise ValueError("current locator strategy and value must appear together")
        if self.disposition is ChangeDisposition.UNCHANGED:
            if self.expected_locator_visible_count != 1 or self.semantic_visible_count != 1:
                raise ValueError("unchanged requires one expected and one semantic match")
        elif self.disposition is ChangeDisposition.LOCATOR_DRIFT:
            if self.expected_locator_visible_count != 0 or self.semantic_visible_count != 1:
                raise ValueError("locator_drift requires absent old locator and one semantic match")
            if not has_current:
                raise ValueError("locator_drift requires one bounded current locator")
        elif self.disposition is ChangeDisposition.MISSING:
            if self.semantic_visible_count != 0:
                raise ValueError("missing requires zero semantic matches")
        elif self.disposition is ChangeDisposition.AMBIGUOUS:
            if self.semantic_visible_count <= 1 and self.expected_locator_visible_count <= 1:
                raise ValueError("ambiguous requires multiple semantic or expected matches")

        expected_impact = {
            ChangeDisposition.UNCHANGED: AutomationImpact.NONE_DETECTED,
            ChangeDisposition.LOCATOR_DRIFT: (
                AutomationImpact.CURRENT_TEST_RISK
                if self.covered_by_current_framework_test
                else AutomationImpact.MAPPED_CONTEXT_STALE
            ),
            ChangeDisposition.MISSING: AutomationImpact.HUMAN_REVIEW_REQUIRED,
            ChangeDisposition.AMBIGUOUS: AutomationImpact.HUMAN_REVIEW_REQUIRED,
        }[self.disposition]
        if self.automation_impact is not expected_impact:
            raise ValueError("automation impact conflicts with disposition and test coverage")
        return self


class FrameworkProbeResult(ContractModel):
    phase: Literal["baseline", "current"]
    collected_test_count: int = Field(ge=1)
    passed_test_count: int = Field(ge=0)
    failed_test_count: int = Field(ge=0)
    infrastructure_error_count: int = Field(ge=0)
    passed: bool

    @model_validator(mode="after")
    def counts_match_status(self) -> "FrameworkProbeResult":
        total = self.passed_test_count + self.failed_test_count + self.infrastructure_error_count
        if total != self.collected_test_count:
            raise ValueError("framework probe counts must equal collected tests")
        if self.passed != (
            self.passed_test_count == self.collected_test_count
            and self.failed_test_count == 0
            and self.infrastructure_error_count == 0
        ):
            raise ValueError("framework probe passed flag conflicts with counts")
        return self


class FrontendChangeReport(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    run_id: Identifier
    inventory_id: Identifier
    generated_at: datetime
    decision: ReportReviewDecision
    observations: tuple[ElementRegressionObservation, ...] = Field(min_length=1)
    stable_count: int = Field(ge=0)
    locator_drift_count: int = Field(ge=0)
    missing_count: int = Field(ge=0)
    ambiguous_count: int = Field(ge=0)
    current_test_risk_count: int = Field(ge=0)
    mapped_context_stale_count: int = Field(ge=0)
    application_bug_claimed: Literal[False] = False
    automatic_patch_created: Literal[False] = False
    context_automatically_modified: Literal[False] = False
    raw_page_persisted: Literal[False] = False
    html_persisted: Literal[False] = False
    screenshot_persisted: Literal[False] = False
    live_llm_used: Literal[False] = False

    @field_validator("generated_at")
    @classmethod
    def generated_at_is_aware(cls, value: datetime) -> datetime:
        return _require_aware(value, "generated_at")

    @model_validator(mode="after")
    def derived_counts_match_observations(self) -> "FrontendChangeReport":
        expected = {
            ChangeDisposition.UNCHANGED: self.stable_count,
            ChangeDisposition.LOCATOR_DRIFT: self.locator_drift_count,
            ChangeDisposition.MISSING: self.missing_count,
            ChangeDisposition.AMBIGUOUS: self.ambiguous_count,
        }
        for disposition, declared in expected.items():
            actual = sum(item.disposition is disposition for item in self.observations)
            if actual != declared:
                raise ValueError(f"{disposition.value} count does not match observations")
        current_risk = sum(
            item.automation_impact is AutomationImpact.CURRENT_TEST_RISK
            for item in self.observations
        )
        mapped_stale = sum(
            item.automation_impact is AutomationImpact.MAPPED_CONTEXT_STALE
            for item in self.observations
        )
        if current_risk != self.current_test_risk_count:
            raise ValueError("current_test_risk_count does not match observations")
        if mapped_stale != self.mapped_context_stale_count:
            raise ValueError("mapped_context_stale_count does not match observations")
        return self


class ProactiveRegressionRun(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    id: Identifier
    profile_id: Identifier
    inventory_id: Identifier
    started_at: datetime
    finished_at: datetime
    status: ProactiveRunStatus
    operator_action_count: int = Field(ge=0, le=3)
    interactive_human_trigger_used: bool
    fixture_decisions_used: bool
    headed_browser_used: bool
    accepted_inventory_reused: bool
    bootstrap_questions_repeated: Literal[False] = False
    baseline_probe: FrameworkProbeResult
    current_probe: FrameworkProbeResult
    report: FrontendChangeReport
    framework_source_fingerprint_before: Sha256
    framework_source_fingerprint_after: Sha256
    original_framework_unchanged: Literal[True] = True
    framework_execution_independent: Literal[True] = True
    application_bug_claimed: Literal[False] = False
    automatic_patch_created: Literal[False] = False
    context_automatically_modified: Literal[False] = False
    live_llm_used: Literal[False] = False
    raw_page_persisted: Literal[False] = False
    measured_savings_claimed: Literal[False] = False

    @field_validator("started_at", "finished_at")
    @classmethod
    def timestamps_are_aware(cls, value: datetime, info) -> datetime:
        return _require_aware(value, info.field_name)

    @model_validator(mode="after")
    def validate_run_evidence(self) -> "ProactiveRegressionRun":
        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot precede started_at")
        if self.report.run_id != self.id:
            raise ValueError("report run_id must match run id")
        if self.report.inventory_id != self.inventory_id:
            raise ValueError("report inventory_id must match run inventory_id")
        if self.framework_source_fingerprint_before != self.framework_source_fingerprint_after:
            raise ValueError("framework source fingerprint changed during proactive regression")
        if self.interactive_human_trigger_used == self.fixture_decisions_used:
            raise ValueError(
                "exactly one of interactive_human_trigger_used and fixture_decisions_used must be true"
            )
        if self.status is ProactiveRunStatus.PASSED:
            if self.operator_action_count != 3:
                raise ValueError("passed run requires exactly three bounded decisions")
            if self.report.decision is not ReportReviewDecision.ACCEPTED:
                raise ValueError("passed run requires an accepted report")
        return self


class ProactiveRegressionAssessment(ContractModel):
    run_id: Identifier
    blockers: tuple[NonEmptyText, ...]
    proactive_regression_verified: bool
    controlled_demo_ready: bool
