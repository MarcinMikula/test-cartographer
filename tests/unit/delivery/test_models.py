import hashlib

import pytest
from pydantic import ValidationError

from test_cartographer.delivery.enums import CreationEvaluationStatus
from test_cartographer.delivery.models import GenerationProfile, SourceChange


def test_generation_profile_contains_explicit_non_secret_bindings(generation_profile):
    assert generation_profile.environment_url_variable == "TEST_CARTOGRAPHER_CATALOG_URL"
    assert generation_profile.test_data_bindings[0].value == "Example"
    assert generation_profile.secret_values_included is False
    assert generation_profile.live_llm_used is False


def test_generation_profile_rejects_duplicate_fixture_keys(generation_profile):
    payload = generation_profile.model_dump(mode="json")
    payload["test_data_bindings"].append(
        {
            "test_data_id": "data_other_query",
            "fixture_key": "search_query",
            "value": "Other",
            "sensitivity": "public",
            "secret": False,
        }
    )
    with pytest.raises(ValidationError, match="fixture keys"):
        GenerationProfile.model_validate(payload)


def test_source_change_preserves_exact_whitespace_and_hash(pending_patch):
    change = next(item for item in pending_patch.changes if item.kind.value == "append_symbol")
    assert change.content.startswith("\n# TestCartographer trace")
    assert change.content.endswith("\n")
    assert hashlib.sha256(change.content.encode()).hexdigest() == change.content_sha256


def test_source_change_rejects_tampered_content(pending_patch):
    payload = pending_patch.changes[0].model_dump(mode="json")
    payload["content"] += "# tampered\n"
    with pytest.raises(ValidationError, match="content_sha256"):
        SourceChange.model_validate(payload)


def test_passed_evaluation_contains_complete_architecture_evidence(passed_evaluation):
    assert passed_evaluation.status is CreationEvaluationStatus.PASSED
    assert passed_evaluation.generated_file_count == 3
    assert passed_evaluation.modified_file_count == 1
    assert passed_evaluation.collected_test_count == 1
    assert passed_evaluation.passed_test_count == 1
    assert passed_evaluation.live_llm_used is False
    assert passed_evaluation.original_framework_unchanged is True
