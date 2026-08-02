import json
from pathlib import Path

from test_cartographer.synthesis.io import load_raw_output
from test_cartographer.synthesis.parser import parse_pom_proposal
from test_cartographer.synthesis.validation import validate_pom_proposal

ROOT = Path(__file__).resolve().parents[3]


def _proposal(name: str):
    return parse_pom_proposal(
        load_raw_output(ROOT / f"testdata/synthesis/raw/{name}")
    )


def test_reference_proposal_is_valid(synthesis_request, valid_proposal) -> None:
    report = validate_pom_proposal(synthesis_request, valid_proposal)
    assert report.valid is True
    assert report.error_count == 0
    assert report.warning_count == 0


def test_prohibited_execution_claim_is_substantive_rejection(synthesis_request) -> None:
    report = validate_pom_proposal(
        synthesis_request,
        _proposal("overreach_public_search.json"),
    )
    assert report.valid is False
    assert [issue.code for issue in report.issues] == ["prohibited_claim"]


def test_unknown_locator_is_rejected(synthesis_request) -> None:
    report = validate_pom_proposal(
        synthesis_request,
        _proposal("unknown_locator_public_search.json"),
    )
    codes = {issue.code for issue in report.issues}
    assert "locator_mismatch" in codes
    assert "unknown_locator_reference" in codes


def test_missing_process_step_is_rejected(synthesis_request) -> None:
    report = validate_pom_proposal(
        synthesis_request,
        _proposal("missing_step_public_search.json"),
    )
    assert "missing_step_coverage" in {issue.code for issue in report.issues}


def test_request_id_mismatch_is_rejected(synthesis_request, valid_proposal) -> None:
    changed = valid_proposal.model_copy(update={"request_id": "synreq_other"})
    report = validate_pom_proposal(synthesis_request, changed)
    assert "request_id_mismatch" in {issue.code for issue in report.issues}


def test_secret_bearing_fixture_is_rejected(synthesis_request, valid_proposal) -> None:
    fixture = valid_proposal.fixtures[0].model_copy(
        update={"secret_values_included": True}
    )
    changed = valid_proposal.model_copy(update={"fixtures": (fixture,)})
    report = validate_pom_proposal(synthesis_request, changed)
    assert "secret_value_claim" in {issue.code for issue in report.issues}


def test_missing_outcome_assertion_is_rejected(synthesis_request, valid_proposal) -> None:
    changed_test = valid_proposal.test.model_copy(update={"assertions": ()})
    # Pydantic min_length is a protocol boundary, so create a different valid
    # outcome reference instead to exercise substantive validation.
    payload = json.loads(valid_proposal.model_dump_json())
    payload["test"]["assertions"][0]["outcome_id"] = "outcome_invented"
    changed = type(valid_proposal).model_validate(payload)
    report = validate_pom_proposal(synthesis_request, changed)
    codes = {issue.code for issue in report.issues}
    assert "unknown_outcome_reference" in codes
    assert "missing_outcome_assertion" in codes


def test_nonblocking_question_is_preserved_as_warning(
    synthesis_request,
    valid_proposal,
) -> None:
    payload = json.loads(valid_proposal.model_dump_json())
    payload["open_questions"] = [
        {
            "id": "question_naming_review",
            "question": "Should class naming follow a project-specific prefix?",
            "related_ids": ["pom_page_catalog"],
            "blocking": False,
        }
    ]
    changed = type(valid_proposal).model_validate(payload)
    report = validate_pom_proposal(synthesis_request, changed)
    assert report.valid is True
    assert report.warning_count == 1
    assert report.issues[0].code == "nonblocking_proposal_question"
