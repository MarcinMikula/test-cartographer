from datetime import datetime

import pytest
from pydantic import ValidationError

from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.expansion.enums import (
    ExpansionDisposition,
    ExpansionReasonCode,
    ExpansionSubjectKind,
)
from test_cartographer.expansion.models import ExpansionPlanItem, ExpansionRequest, ExpansionRun


def test_request_rejects_duplicate_targets(expansion_request):
    payload = expansion_request.model_dump(mode="python")
    payload["target_element_ids"] = ("el_sort_results", "el_sort_results")
    with pytest.raises(ValidationError, match="target_element_ids must be unique"):
        ExpansionRequest.model_validate(payload)


def test_request_requires_timezone_aware_timestamp(expansion_request):
    payload = expansion_request.model_dump(mode="python")
    payload["requested_at"] = datetime(2026, 8, 9, 8, 0)
    with pytest.raises(ValidationError, match="timezone offset"):
        ExpansionRequest.model_validate(payload)


def test_reuse_item_requires_confirmed_or_observed_authority():
    with pytest.raises(ValidationError, match="confirmed or observed"):
        ExpansionPlanItem(
            id="exp_bad_reuse",
            subject_kind=ExpansionSubjectKind.PROCESS_VALUE,
            subject_ref="target_process.risk",
            source_id="proc_search_catalog",
            knowledge_status=KnowledgeStatus.PROVIDED,
            disposition=ExpansionDisposition.REUSE,
            reason_code=ExpansionReasonCode.AUTHORIZED_CURRENT_KNOWLEDGE,
        )


def test_framework_snapshot_item_cannot_masquerade_as_context_knowledge():
    with pytest.raises(ValidationError, match="must not masquerade"):
        ExpansionPlanItem(
            id="exp_snapshot_bad",
            subject_kind=ExpansionSubjectKind.FRAMEWORK_SNAPSHOT,
            subject_ref="framework.snapshot",
            source_id="snapshot_expansion",
            knowledge_status=KnowledgeStatus.CONFIRMED,
            disposition=ExpansionDisposition.REUSE,
            reason_code=ExpansionReasonCode.FRAMEWORK_SNAPSHOT_BOUND,
        )


def test_real_human_run_cannot_use_fixture_decisions(passed_real_run):
    run = passed_real_run
    payload = run.model_dump(mode="python")
    payload["fixture_decisions_used"] = True
    with pytest.raises(ValidationError, match="cannot use fixture decisions"):
        ExpansionRun.model_validate(payload)


def test_passed_run_requires_existing_symbol_extension_evidence(passed_fixture_run):
    run = passed_fixture_run
    payload = run.model_dump(mode="python")
    payload["framework_symbols_extended"] = 0
    payload["existing_page_object_extended"] = False
    with pytest.raises(ValidationError, match="existing framework symbol extension"):
        ExpansionRun.model_validate(payload)


def test_passed_run_requires_hash_bound_replacement_and_preflight(passed_fixture_run):
    run = passed_fixture_run
    payload = run.model_dump(mode="python")
    payload["hash_bound_source_replacement_used"] = False
    with pytest.raises(ValidationError, match="hash-bound"):
        ExpansionRun.model_validate(payload)
