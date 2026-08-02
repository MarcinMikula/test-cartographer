import json

import pytest

from test_cartographer.synthesis.parser import (
    ProposalParseError,
    parse_pom_proposal,
)


def test_valid_raw_output_parses(valid_raw_output) -> None:
    proposal = parse_pom_proposal(valid_raw_output)
    assert proposal.id == "proposal_public_search"
    assert proposal.schema_version == "0.1"


def test_markdown_fence_is_rejected() -> None:
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal("```json\n{}\n```")
    assert error.value.code == "markdown_fence"


def test_invalid_json_is_rejected() -> None:
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal('{"schema_version": "0.1",}')
    assert error.value.code == "invalid_json"


def test_empty_output_is_rejected() -> None:
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal("   ")
    assert error.value.code == "empty_output"


def test_non_object_root_is_rejected() -> None:
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal("[]")
    assert error.value.code == "root_not_object"


def test_duplicate_object_key_is_rejected(valid_raw_output) -> None:
    raw = valid_raw_output.replace(
        '"schema_version": "0.1",',
        '"schema_version": "0.1",\n  "schema_version": "0.1",',
        1,
    )
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal(raw)
    assert error.value.code == "duplicate_key"


def test_schema_version_drift_is_rejected(valid_raw_output) -> None:
    raw = valid_raw_output.replace('"schema_version": "0.1"', '"schema_version": "0.2"', 1)
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal(raw)
    assert error.value.code == "schema_validation"


def test_unexpected_field_is_rejected(valid_raw_output) -> None:
    payload = json.loads(valid_raw_output)
    payload["target_file"] = "pages/catalog.py"
    with pytest.raises(ProposalParseError) as error:
        parse_pom_proposal(json.dumps(payload))
    assert error.value.code == "schema_validation"
