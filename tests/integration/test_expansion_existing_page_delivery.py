from __future__ import annotations

import hashlib
import shutil
from datetime import datetime, timezone
from pathlib import Path

import pytest

from test_cartographer.adaptation.enums import (
    AdaptationOperationKind,
    AdaptationPlanStatus,
    AdaptationReviewDecision,
    PythonSymbolKind,
)
from test_cartographer.adaptation.models import WorkspaceProfile
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.enums import ActionKind, EvidenceSourceType, KnowledgeStatus, LocatorStrategy, SensitivityLevel
from test_cartographer.delivery.apply import apply_code_patch
from test_cartographer.delivery.enums import CodePatchStatus, PatchReviewDecision, SourceChangeKind
from test_cartographer.delivery.generation import build_code_patch
from test_cartographer.delivery.models import (
    CodePatch,
    FrameworkSymbolRequirement,
    GenerationProfile,
    TestDataBinding as DeliveryTestDataBinding,
)
from test_cartographer.synthesis.enums import ProposalOwnerKind, ProposalReviewDecision, SynthesisRunStatus
from test_cartographer.synthesis.models import (
    AuthorizedAction,
    AuthorizedElement,
    AuthorizedEvidenceReference,
    AuthorizedLocator,
    AuthorizedOutcome,
    AuthorizedPage,
    AuthorizedStep,
    AuthorizedTestData,
    AuthorizedValue,
    BoundedSynthesisRequest,
    PomProposal,
    ProposalClaimFlags,
    ProposalValidationReport,
    ProposedAction,
    ProposedAssertion,
    ProposedFixture,
    ProposedMethod,
    ProposedPageObject,
    ProposedTest,
    SynthesisRun,
)

NOW = datetime(2026, 8, 9, 8, 0, tzinfo=timezone.utc)
EVIDENCE_ID = "ev_sort"


def _authorized(value: str) -> AuthorizedValue:
    return AuthorizedValue(
        value=value,
        status=KnowledgeStatus.OBSERVED,
        evidence_ids=(EVIDENCE_ID,),
        sensitivity=SensitivityLevel.PUBLIC,
    )


def _build_framework(root: Path) -> None:
    (root / "pages").mkdir(parents=True)
    (root / "components").mkdir(parents=True)
    (root / "tests/e2e").mkdir(parents=True)
    (root / "README.md").write_text("# framework\n", encoding="utf-8")
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


def _accepted_sort_run() -> SynthesisRun:
    sort_element = AuthorizedElement(
        id="el_sort_results",
        owner_id="page_catalog",
        name=_authorized("Sort results"),
        semantic_role=_authorized("Button named Sort results"),
        primary_locator=AuthorizedLocator(
            id="loc_sort_results_current",
            strategy=LocatorStrategy.TEST_ID,
            value=_authorized("catalog-sort-control"),
        ),
    )
    results_element = AuthorizedElement(
        id="el_results_list",
        owner_id="page_catalog",
        name=_authorized("Results list"),
        semantic_role=_authorized("List containing catalog items"),
        primary_locator=AuthorizedLocator(
            id="loc_results_list_test_id",
            strategy=LocatorStrategy.TEST_ID,
            value=_authorized("catalog-results"),
        ),
    )
    request = BoundedSynthesisRequest(
        id="synreq_sort",
        context_id="ctx_sort_candidate",
        created_at=NOW,
        application_id="app_catalog",
        application_name=_authorized("Catalog"),
        environment=_authorized("Local"),
        process_id="proc_sort_catalog",
        process_name=_authorized("Sort catalog results"),
        purpose=_authorized("Order catalog results"),
        risk=_authorized("Wrong order can mislead users"),
        role=_authorized("Visitor"),
        preconditions=(_authorized("Catalog results are visible"),),
        steps=(
            AuthorizedStep(
                id="step_open",
                order=1,
                page_id="page_catalog",
                intent=_authorized("Open catalog"),
                action=AuthorizedAction(kind=ActionKind.NAVIGATE),
                expected_state=_authorized("Catalog is visible"),
            ),
            AuthorizedStep(
                id="step_sort",
                order=2,
                page_id="page_catalog",
                intent=_authorized("Sort results"),
                action=AuthorizedAction(kind=ActionKind.CLICK, target_element_id="el_sort_results"),
                expected_state=_authorized("Results are sorted"),
            ),
            AuthorizedStep(
                id="step_read",
                order=3,
                page_id="page_catalog",
                intent=_authorized("Read sorted results"),
                action=AuthorizedAction(kind=ActionKind.READ, target_element_id="el_results_list"),
                expected_state=_authorized("Sorted results are visible"),
            ),
        ),
        outcomes=(
            AuthorizedOutcome(
                id="outcome_sorted",
                statement=_authorized("Results appear in expected order"),
                related_element_ids=("el_results_list",),
            ),
        ),
        pages=(
            AuthorizedPage(
                id="page_catalog",
                name=_authorized("Catalog page"),
                element_ids=("el_sort_results", "el_results_list"),
            ),
        ),
        elements=(sort_element, results_element),
        test_data=(
            AuthorizedTestData(
                id="data_expected_order",
                name=_authorized("Expected order"),
                description=_authorized("Expected visible sorted result fragment"),
                symbolic_ref="expected_sort_order",
                sensitivity=SensitivityLevel.PUBLIC,
            ),
        ),
        evidence=(
            AuthorizedEvidenceReference(
                id=EVIDENCE_ID,
                source_type=EvidenceSourceType.APPLICATION,
                summary="Controlled sort evidence.",
                sensitivity=SensitivityLevel.PUBLIC,
            ),
        ),
        prohibited_claims=("Do not claim execution success before running the test.",),
    )
    proposal = PomProposal(
        id="proposal_sort",
        request_id=request.id,
        context_id=request.context_id,
        summary="Extend CatalogPage with sorting.",
        pages=(
            ProposedPageObject(
                id="pom_page_catalog_sort",
                class_name="CatalogPage",
                source_page_id="page_catalog",
                method_ids=("method_open_catalog", "method_apply_sort", "method_read_results"),
            ),
        ),
        methods=(
            ProposedMethod(
                id="method_open_catalog",
                name="open_catalog",
                owner_kind=ProposalOwnerKind.PAGE,
                owner_source_id="page_catalog",
                intent="Open catalog.",
                actions=(ProposedAction(step_id="step_open", kind=ActionKind.NAVIGATE),),
            ),
            ProposedMethod(
                id="method_apply_sort",
                name="apply_sort",
                owner_kind=ProposalOwnerKind.PAGE,
                owner_source_id="page_catalog",
                intent="Apply result sorting.",
                actions=(
                    ProposedAction(
                        step_id="step_sort",
                        kind=ActionKind.CLICK,
                        target_element_id="el_sort_results",
                        locator_id="loc_sort_results_current",
                    ),
                ),
            ),
            ProposedMethod(
                id="method_read_results",
                name="read_results",
                owner_kind=ProposalOwnerKind.PAGE,
                owner_source_id="page_catalog",
                intent="Read sorted results.",
                actions=(
                    ProposedAction(
                        step_id="step_read",
                        kind=ActionKind.READ,
                        target_element_id="el_results_list",
                        locator_id="loc_results_list_test_id",
                    ),
                ),
            ),
        ),
        fixtures=(
            ProposedFixture(
                id="fixture_catalog_context",
                name="catalog_context",
                purpose="Provide browser and data.",
                uses_role_from_context=True,
                uses_environment_from_context=True,
                secret_values_included=False,
            ),
        ),
        test=ProposedTest(
            id="test_sort_catalog",
            name="test_sort_catalog",
            process_id="proc_sort_catalog",
            fixture_ids=("fixture_catalog_context",),
            method_ids=("method_open_catalog", "method_apply_sort", "method_read_results"),
            assertions=(
                ProposedAssertion(
                    id="assert_sorted",
                    outcome_id="outcome_sorted",
                    page_id="page_catalog",
                    related_element_ids=("el_results_list",),
                    intent="Verify sorted results.",
                ),
            ),
        ),
        claim_flags=ProposalClaimFlags(),
    )
    return SynthesisRun(
        id="synrun_sort",
        request=request,
        prompt_sha256="0" * 64,
        raw_output="{}",
        status=SynthesisRunStatus.ACCEPTED,
        proposal=proposal,
        validation=ProposalValidationReport(),
        decision=ProposalReviewDecision.ACCEPTED,
        started_at=NOW,
        completed_at=NOW,
        reviewed_at=NOW,
        review_seconds=1.0,
    )


def _build_extension(tmp_path):
    framework = tmp_path / "framework"
    _build_framework(framework)
    profile = WorkspaceProfile(
        id="workspace_sort",
        repository_label="Sort expansion framework",
        root_marker_files=("README.md",),
        allowed_roots=("pages", "components", "tests/e2e"),
    )
    snapshot = inspect_framework(framework, profile, snapshot_id="snapshot_sort", captured_at=NOW)
    run = _accepted_sort_run()
    plan = build_adaptation_plan(run, profile, snapshot, plan_id="adapt_sort", created_at=NOW)
    page_op = next(item for item in plan.operations if item.symbol_name == "CatalogPage")
    accepted_plan = plan.model_copy(
        update={
            "status": AdaptationPlanStatus.ACCEPTED,
            "decision": AdaptationReviewDecision.ACCEPTED,
            "reviewed_at": NOW,
            "review_seconds": 1.0,
        }
    )
    generation = GenerationProfile(
        id="gen_sort",
        workspace_profile_id=profile.id,
        environment_url_variable="BASE_URL",
        required_framework_symbols=(
            FrameworkSymbolRequirement(
                path="pages/base_page.py",
                symbol_name="BasePage",
                symbol_kind=PythonSymbolKind.CLASS,
            ),
        ),
        test_data_bindings=(
            DeliveryTestDataBinding(
                test_data_id="data_expected_order",
                fixture_key="expected_sort_order",
                value="Alpha Beta Zulu",
                sensitivity=SensitivityLevel.PUBLIC,
            ),
        ),
        browser_headless=True,
    )
    patch = build_code_patch(
        run,
        accepted_plan,
        profile,
        generation,
        snapshot,
        framework,
        patch_id="patch_sort",
        created_at=NOW,
    )
    return framework, profile, snapshot, page_op, patch


def test_existing_catalog_page_is_extended_with_only_missing_sort_members(tmp_path):
    _, _, _, page_op, _ = _build_extension(tmp_path)
    assert page_op.kind is AdaptationOperationKind.EXTEND_SYMBOL
    assert page_op.method_names == ("apply_sort",)
    assert page_op.property_names == ("sort_results",)


def test_extension_generates_hash_bound_replacement_and_new_test(tmp_path):
    framework, _, _, _, patch = _build_extension(tmp_path)
    page_change = next(item for item in patch.changes if item.target_path == "pages/catalog_page.py")
    assert page_change.kind is SourceChangeKind.REPLACE_FILE
    assert page_change.expected_before_sha256 == hashlib.sha256(
        (framework / "pages/catalog_page.py").read_bytes()
    ).hexdigest()
    assert "def apply_sort(self) -> None:" in page_change.content
    assert "def sort_results(self) -> Locator:" in page_change.content
    assert page_change.content.count("def open_catalog") == 1
    assert page_change.content.count("def read_results") == 1
    test_change = next(
        item
        for item in patch.changes
        if item.kind is SourceChangeKind.CREATE_FILE
        and item.target_path == "tests/e2e/test_sort_catalog.py"
    )
    assert "explicitly supplied expected result" in test_change.content
    assert "explicitly supplied search query" not in test_change.content


def test_accepted_extension_applies_only_to_sandbox_copy(tmp_path):
    framework, profile, snapshot, _, patch = _build_extension(tmp_path)
    original = (framework / "pages/catalog_page.py").read_bytes()
    sandbox = tmp_path / "sandbox"
    shutil.copytree(framework, sandbox)
    accepted = CodePatch.model_validate(
        patch.model_copy(
            update={
                "status": CodePatchStatus.ACCEPTED,
                "decision": PatchReviewDecision.ACCEPTED,
                "reviewed_at": NOW,
                "review_seconds": 1.0,
            }
        ).model_dump(mode="python")
    )
    report = apply_code_patch(
        accepted,
        profile,
        snapshot,
        sandbox,
        application_id="apply_sort",
        applied_at=NOW,
    )
    assert report.preflight_passed is True
    assert "def apply_sort(self) -> None:" in (sandbox / "pages/catalog_page.py").read_text(encoding="utf-8")
    assert (framework / "pages/catalog_page.py").read_bytes() == original


def test_source_drift_rejects_replace_before_any_write(tmp_path):
    framework, profile, snapshot, _, patch = _build_extension(tmp_path)
    sandbox = tmp_path / "sandbox"
    shutil.copytree(framework, sandbox)
    accepted = CodePatch.model_validate(
        patch.model_copy(
            update={
                "status": CodePatchStatus.ACCEPTED,
                "decision": PatchReviewDecision.ACCEPTED,
                "reviewed_at": NOW,
                "review_seconds": 1.0,
            }
        ).model_dump(mode="python")
    )
    target = sandbox / "pages/catalog_page.py"
    target.write_text(target.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
    before = target.read_bytes()
    with pytest.raises(ValueError, match="fingerprint changed"):
        apply_code_patch(
            accepted,
            profile,
            snapshot,
            sandbox,
            application_id="apply_drifted_sort",
            applied_at=NOW,
        )
    assert target.read_bytes() == before
