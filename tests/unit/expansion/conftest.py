from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.enums import (
    ActionKind,
    EvidenceSourceType,
    KnowledgeStatus,
    LocatorStrategy,
    SensitivityLevel,
)
from test_cartographer.context.models import (
    ApplicationContext,
    ContextBundle,
    Evidence,
    ExpectedOutcome,
    KnowledgeText,
    LocatorCandidate,
    PageContext,
    ProcessContext,
    ProcessStep,
    TestDataRequirement,
    UIAction,
    UIElement,
)
from test_cartographer.expansion.assessment import assess_expansion_run
from test_cartographer.expansion.context_builder import (
    build_candidate_expansion_context,
    observed_element_from_regression,
)
from test_cartographer.expansion.enums import ExpansionRunStatus
from test_cartographer.expansion.fingerprints import context_sha256
from test_cartographer.expansion.models import ExpansionRequest, ExpansionRun
from test_cartographer.expansion.planner import build_expansion_plan
from test_cartographer.expansion.review import accept_expansion_plan
from test_cartographer.proactive_regression.enums import (
    AuthenticationMode,
    AutomationImpact,
    ChangeDisposition,
    InventoryReviewDecision,
    ReportReviewDecision,
)
from test_cartographer.proactive_regression.models import (
    ApprovedObservationItem,
    ElementRegressionObservation,
    FrontendChangeReport,
    ObservationBudget,
    ObservationInventory,
    ObservedAttribute,
)


@pytest.fixture
def fixed_now() -> datetime:
    return datetime(2026, 8, 9, 8, 0, tzinfo=timezone.utc)


def _knowledge(value: str, *, status: KnowledgeStatus = KnowledgeStatus.CONFIRMED, evidence_ids=("ev_base",)) -> KnowledgeText:
    return KnowledgeText(
        value=value,
        status=status,
        evidence_ids=evidence_ids,
        sensitivity=SensitivityLevel.PUBLIC,
    )


@pytest.fixture
def base_context(fixed_now: datetime) -> ContextBundle:
    evidence = Evidence(
        id="ev_base",
        source_type=EvidenceSourceType.HUMAN,
        source_ref="human:accepted",
        summary="Accepted base context.",
        captured_at=fixed_now,
        sensitivity=SensitivityLevel.PUBLIC,
        content_sha256="1" * 64,
    )
    application = ApplicationContext(
        id="app_catalog",
        name=_knowledge("Catalog"),
        environment=_knowledge("Local"),
        base_url=_knowledge("http://127.0.0.1"),
    )
    results = UIElement(
        id="el_results_list",
        owner_id="page_catalog",
        name=_knowledge("Results list", status=KnowledgeStatus.OBSERVED),
        semantic_role=_knowledge("List containing catalog items", status=KnowledgeStatus.OBSERVED),
        locator_candidates=(
            LocatorCandidate(
                id="loc_results",
                strategy=LocatorStrategy.TEST_ID,
                value=_knowledge("catalog-results", status=KnowledgeStatus.OBSERVED),
                primary=True,
            ),
        ),
    )
    page = PageContext(
        id="page_catalog",
        name=_knowledge("Catalog page", status=KnowledgeStatus.OBSERVED),
        route=_knowledge("/catalog", status=KnowledgeStatus.OBSERVED),
        element_ids=("el_results_list",),
    )
    process = ProcessContext(
        id="proc_search_catalog",
        name=_knowledge("Search catalog"),
        purpose=_knowledge("Find items"),
        risk=_knowledge("Missing items"),
        role=_knowledge("Visitor"),
        preconditions=(_knowledge("Catalog available"),),
        steps=(
            ProcessStep(
                id="step_search_read",
                order=1,
                page_id="page_catalog",
                intent=_knowledge("Read results"),
                action=UIAction(kind=ActionKind.READ, target_element_id="el_results_list"),
                expected_state=_knowledge("Results visible", status=KnowledgeStatus.OBSERVED),
            ),
        ),
        expected_outcomes=(
            ExpectedOutcome(
                id="out_search",
                statement=_knowledge("Results visible"),
                related_element_ids=("el_results_list",),
            ),
        ),
    )
    return ContextBundle(
        id="ctx_search",
        title="Accepted search context",
        created_at=fixed_now,
        updated_at=fixed_now,
        application=application,
        process=process,
        pages=(page,),
        elements=(results,),
        evidence=(evidence,),
    )


@pytest.fixture
def workspace_profile() -> WorkspaceProfile:
    return WorkspaceProfile(
        id="workspace_expansion",
        repository_label="Expansion reference framework",
        root_marker_files=("README.md",),
        allowed_roots=("pages", "components", "tests/e2e"),
    )


@pytest.fixture
def framework_root(tmp_path: Path) -> Path:
    root = tmp_path / "framework"
    (root / "pages").mkdir(parents=True)
    (root / "components").mkdir(parents=True)
    (root / "tests/e2e").mkdir(parents=True)
    (root / "README.md").write_text("# expansion framework\n", encoding="utf-8")
    (root / "components/__init__.py").write_text("", encoding="utf-8")
    (root / "pages/base_page.py").write_text(
        "from playwright.sync_api import Page\n\n"
        "class BasePage:\n"
        "    def __init__(self, page: Page, base_url: str = '') -> None:\n"
        "        self.page = page\n"
        "        self.base_url = base_url\n\n"
        "    def open(self) -> None:\n"
        "        self.page.goto(self.base_url)\n",
        encoding="utf-8",
    )
    (root / "pages/catalog_page.py").write_text(
        "from playwright.sync_api import Locator, Page\n\n"
        "from pages.base_page import BasePage\n\n"
        "class CatalogPage(BasePage):\n"
        "    def __init__(self, page: Page, base_url: str = '') -> None:\n"
        "        super().__init__(page, base_url=base_url)\n\n"
        "    @property\n"
        "    def results_list(self) -> Locator:\n"
        "        return self.page.get_by_test_id('catalog-results')\n\n"
        "    def open_catalog(self) -> None:\n"
        "        self.open()\n\n"
        "    def read_results(self) -> str:\n"
        "        return self.results_list.inner_text()\n",
        encoding="utf-8",
    )
    (root / "tests/e2e/conftest.py").write_text(
        "import pytest\n\n@pytest.fixture\ndef catalog_context():\n    return {}\n",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def framework_snapshot(framework_root: Path, workspace_profile: WorkspaceProfile, fixed_now: datetime):
    return inspect_framework(
        framework_root,
        workspace_profile,
        snapshot_id="snapshot_expansion",
        captured_at=fixed_now,
    )


@pytest.fixture
def observation_inventory(base_context: ContextBundle, fixed_now: datetime) -> ObservationInventory:
    item = ApprovedObservationItem(
        id="inventory_sort",
        page_id="page_catalog",
        element_id="el_sort_results",
        route="/catalog",
        semantic_role="button",
        accessible_name="Sort results",
        primary_locator_strategy=LocatorStrategy.TEST_ID,
        primary_locator_value="catalog-sort",
        covered_by_current_framework_test=False,
    )
    return ObservationInventory(
        id="inventory_catalog",
        context_bundle_id=base_context.id,
        process_id=base_context.process.id,
        base_origin="http://127.0.0.1",
        allowed_routes=("/catalog",),
        allowed_actions=("navigate", "observe"),
        authentication_mode=AuthenticationMode.NONE,
        sensitivity=SensitivityLevel.PUBLIC,
        budget=ObservationBudget(
            max_pages=1,
            max_elements=1,
            navigation_timeout_ms=30000,
            locator_timeout_ms=2000,
        ),
        review_decision=InventoryReviewDecision.ACCEPTED,
        human_approved=True,
        accepted_at=fixed_now,
        items=(item,),
    )


@pytest.fixture
def drift_observation() -> ElementRegressionObservation:
    return ElementRegressionObservation(
        item_id="inventory_sort",
        element_id="el_sort_results",
        disposition=ChangeDisposition.LOCATOR_DRIFT,
        automation_impact=AutomationImpact.MAPPED_CONTEXT_STALE,
        covered_by_current_framework_test=False,
        expected_locator_strategy=LocatorStrategy.TEST_ID,
        expected_locator_value="catalog-sort",
        expected_locator_visible_count=0,
        semantic_visible_count=1,
        current_locator_strategy=LocatorStrategy.TEST_ID,
        current_locator_value="catalog-sort-control",
        observed_attributes=(ObservedAttribute(name="data-testid", value="catalog-sort-control"),),
        observation_sha256="2" * 64,
    )


@pytest.fixture
def drift_report(observation_inventory, drift_observation, fixed_now) -> FrontendChangeReport:
    return FrontendChangeReport(
        id="report_catalog",
        run_id="proactive_catalog",
        inventory_id=observation_inventory.id,
        generated_at=fixed_now,
        decision=ReportReviewDecision.ACCEPTED,
        observations=(drift_observation,),
        stable_count=0,
        locator_drift_count=1,
        missing_count=0,
        ambiguous_count=0,
        current_test_risk_count=0,
        mapped_context_stale_count=1,
    )


@pytest.fixture
def expansion_request(base_context, workspace_profile, framework_snapshot, drift_report, fixed_now):
    return ExpansionRequest(
        id="exp_request_sort",
        base_context_id=base_context.id,
        base_context_sha256=context_sha256(base_context),
        workspace_profile_id=workspace_profile.id,
        framework_snapshot_id=framework_snapshot.id,
        framework_snapshot_fingerprint=framework_snapshot.root_fingerprint,
        target_process_id="proc_sort_catalog",
        target_process_name="Sort catalog results",
        human_intent="Add an automated process for sorting catalog results.",
        target_element_ids=("el_sort_results",),
        requested_at=fixed_now,
        proactive_report_id=drift_report.id,
    )


@pytest.fixture
def expansion_plan(expansion_request, base_context, framework_snapshot, observation_inventory, drift_report, fixed_now):
    return build_expansion_plan(
        expansion_request,
        base_context,
        framework_snapshot,
        plan_id="exp_plan_sort",
        created_at=fixed_now,
        inventory=observation_inventory,
        change_report=drift_report,
    )


@pytest.fixture
def accepted_expansion_plan(expansion_plan, fixed_now):
    return accept_expansion_plan(expansion_plan, reviewed_at=fixed_now, review_seconds=1.0)


def _human_knowledge(value: str) -> KnowledgeText:
    return KnowledgeText(
        value=value,
        status=KnowledgeStatus.CONFIRMED,
        evidence_ids=("ev_sort_human",),
        sensitivity=SensitivityLevel.PUBLIC,
    )


@pytest.fixture
def target_process(base_context) -> ProcessContext:
    return ProcessContext(
        id="proc_sort_catalog",
        name=_human_knowledge("Sort catalog results"),
        purpose=_human_knowledge("Order visible catalog results"),
        risk=_human_knowledge("Wrong ordering can mislead the visitor"),
        role=base_context.process.role,
        preconditions=base_context.process.preconditions,
        steps=(
            ProcessStep(
                id="step_open_catalog_sort",
                order=1,
                page_id="page_catalog",
                intent=_human_knowledge("Open the catalog"),
                action=UIAction(kind=ActionKind.NAVIGATE),
                expected_state=_human_knowledge("Catalog is visible"),
            ),
            ProcessStep(
                id="step_apply_sort",
                order=2,
                page_id="page_catalog",
                intent=_human_knowledge("Apply result sorting"),
                action=UIAction(kind=ActionKind.CLICK, target_element_id="el_sort_results"),
                expected_state=_human_knowledge("Result order changes"),
            ),
            ProcessStep(
                id="step_read_sorted",
                order=3,
                page_id="page_catalog",
                intent=_human_knowledge("Read the sorted results"),
                action=UIAction(kind=ActionKind.READ, target_element_id="el_results_list"),
                expected_state=_human_knowledge("Sorted results are visible"),
            ),
        ),
        expected_outcomes=(
            ExpectedOutcome(
                id="out_sorted",
                statement=_human_knowledge("Results are shown in expected order"),
                related_element_ids=("el_results_list",),
            ),
        ),
    )


@pytest.fixture
def candidate_context(
    expansion_request,
    accepted_expansion_plan,
    base_context,
    target_process,
    observation_inventory,
    drift_observation,
    fixed_now,
):
    item = observation_inventory.items[0]
    fresh_sort, application_evidence = observed_element_from_regression(
        item,
        drift_observation,
        evidence_id="ev_sort_fresh",
        observed_at=fixed_now,
    )
    human_evidence = Evidence(
        id="ev_sort_human",
        source_type=EvidenceSourceType.HUMAN,
        source_ref="human:sort-intent",
        summary="Human confirmed process-specific sort meaning.",
        captured_at=fixed_now,
        sensitivity=SensitivityLevel.PUBLIC,
        content_sha256="3" * 64,
    )
    test_data = TestDataRequirement(
        id="data_expected_order",
        name=_human_knowledge("Expected sorted result"),
        description=_human_knowledge("Expected visible ordered result fragment"),
        symbolic_ref="expected_sort_order",
        sensitivity=SensitivityLevel.PUBLIC,
    )
    return build_candidate_expansion_context(
        expansion_request,
        accepted_expansion_plan,
        base_context,
        target_process,
        candidate_context_id="ctx_sort_candidate",
        title="Sort expansion candidate",
        created_at=fixed_now,
        observed_elements=(fresh_sort,),
        additional_evidence=(application_evidence, human_evidence),
        test_data=(test_data,),
    )


def make_passed_run(*, fixed_now: datetime, interactive: bool) -> ExpansionRun:
    return ExpansionRun(
        id="exp_run_real" if interactive else "exp_run_fixture",
        request_id="exp_request_sort",
        plan_id="exp_plan_sort",
        base_context_id="ctx_search",
        base_context_sha256="a" * 64,
        candidate_context_id="ctx_sort_candidate",
        candidate_context_sha256="b" * 64,
        framework_snapshot_id="snapshot_expansion",
        framework_snapshot_fingerprint="c" * 64,
        started_at=fixed_now,
        finished_at=fixed_now,
        status=ExpansionRunStatus.PASSED,
        synthesis_run_id="synrun_sort",
        adaptation_plan_id="adapt_sort",
        code_patch_id="patch_sort",
        application_report_id="apply_sort",
        target_test="tests/e2e/test_sort_catalog.py",
        reused_knowledge_item_count=7,
        process_specific_questions_asked=3,
        new_observation_count=0,
        reobservation_count=1,
        review_item_count=1,
        blocked_item_count=0,
        framework_symbols_reused=1,
        framework_symbols_extended=1,
        framework_symbols_added=1,
        existing_tests_preserved=1,
        new_tests_added=1,
        operator_action_count=5 if interactive else 5,
        active_operator_seconds=8.0,
        browser_seconds=2.0,
        verification_seconds=4.0,
        live_llm_calls=0,
        interactive_human_trigger_used=interactive,
        headed_browser_used=interactive,
        fixture_decisions_used=not interactive,
        candidate_context_reviewed=True,
        existing_creation_pipeline_reused=True,
        existing_page_object_extended=True,
        method_property_collision_protection=True,
        hash_bound_source_replacement_used=True,
        source_drift_preflight_enforced=True,
        framework_execution_independent=True,
        base_context_unchanged=True,
        original_framework_unchanged=True,
    )


@pytest.fixture
def passed_fixture_run(fixed_now):
    return make_passed_run(fixed_now=fixed_now, interactive=False)


@pytest.fixture
def passed_real_run(fixed_now):
    return make_passed_run(fixed_now=fixed_now, interactive=True)
