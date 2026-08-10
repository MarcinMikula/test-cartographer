from datetime import datetime, timedelta, timezone

import pytest

from test_cartographer.context.enums import SensitivityLevel
from test_cartographer.validation.enums import (
    ValidationArtefactKind,
    ValidationArtefactProducer,
    ValidationAuthenticationRequirement,
    ValidationOperatorDifficulty,
    ValidationResultConfidence,
    ValidationRunCompletion,
    ValidationTargetControl,
    ValidationTargetDifficulty,
    ValidationTargetFamiliarity,
    ValidationWorkflowKind,
    ValidationWorkflowReuseIntent,
)
from test_cartographer.validation.models import (
    ValidationEvidenceEntry,
    ValidationOperatorAssessment,
    ValidationProductReference,
    ValidationRuntimeEnvironment,
    ValidationTiming,
)
from test_cartographer.validation.service import (
    create_validation_run,
    create_validation_target_profile,
)


@pytest.fixture
def accepted_at():
    return datetime(2026, 8, 10, 17, 0, tzinfo=timezone.utc)


@pytest.fixture
def target_profile():
    return create_validation_target_profile(
        profile_id="public_catalog_validation",
        label="Public catalog controlled rehearsal",
        target_url="http://127.0.0.1:8765/catalog",
        difficulty=ValidationTargetDifficulty.SIMPLE,
        control=ValidationTargetControl.PROJECT_CONTROLLED,
        authentication=ValidationAuthenticationRequirement.NONE,
        process_label="Search public catalog",
        allowed_actions=("open catalog", "search catalog"),
        prohibited_actions=("destructive actions",),
        authorization_statement="Controlled local target approved for validation rehearsal.",
        operator_authorization_confirmed=True,
        sensitivity=SensitivityLevel.INTERNAL,
    )


@pytest.fixture
def runtime():
    return ValidationRuntimeEnvironment(
        operating_system="Windows",
        python_version="3.11",
        browser_name="Chromium",
        browser_version="151",
        llm_provider="replay",
        llm_model="fixture",
    )


@pytest.fixture
def timing():
    return ValidationTiming(
        elapsed_seconds=30.0,
        setup_active_seconds=5.0,
        intake_active_seconds=4.0,
        review_active_seconds=6.0,
        correction_active_seconds=0.0,
        system_wait_seconds=10.0,
    )


@pytest.fixture
def operator_assessment():
    return ValidationOperatorAssessment(
        difficulty=ValidationOperatorDifficulty.MODERATE,
        confidence_in_result=ValidationResultConfidence.HIGH,
        would_reuse_workflow=ValidationWorkflowReuseIntent.YES,
        prior_target_familiarity=ValidationTargetFamiliarity.SEEN_BEFORE,
    )


@pytest.fixture
def product_ref():
    return ValidationProductReference(
        git_commit="f9218bc09e80ba513a485c42864c1ba96dace329",
        version="0.16.0",
    )


@pytest.fixture
def validation_run(
    target_profile,
    accepted_at,
    runtime,
    timing,
    operator_assessment,
    product_ref,
):
    return create_validation_run(
        run_id="validation_run_one",
        target_profile=target_profile,
        workflow=ValidationWorkflowKind.TESTCARTOGRAPHER,
        product_ref=product_ref,
        started_at=accepted_at,
        finished_at=accepted_at + timedelta(seconds=30),
        runtime=runtime,
        timing=timing,
        findings=(),
        completion=ValidationRunCompletion.COMPLETED,
        operator_assessment=operator_assessment,
    )


@pytest.fixture
def evidence_entry():
    return ValidationEvidenceEntry(
        relative_path="evidence/context-bundle.json",
        sha256="a" * 64,
        artefact_kind=ValidationArtefactKind.CONTEXT_BUNDLE,
        sensitivity=SensitivityLevel.INTERNAL,
        producer=ValidationArtefactProducer.TESTCARTOGRAPHER,
    )
