from pathlib import Path

from test_cartographer.context.enums import ActionKind
from test_cartographer.creation_flow.external_template import (
    render_external_single_page_proposal,
)
from test_cartographer.synthesis.io import load_synthesis_request
from test_cartographer.synthesis.models import BoundedSynthesisRequest
from test_cartographer.synthesis.parser import parse_pom_proposal
from test_cartographer.synthesis.validation import validate_pom_proposal

ROOT = Path(__file__).resolve().parents[3]


def _external_request() -> BoundedSynthesisRequest:
    source = load_synthesis_request(ROOT / "testdata/synthesis/request/public_search.json")
    navigate = source.steps[0]
    read = source.steps[-1].model_copy(update={"order": 2})
    assert navigate.action.kind is ActionKind.NAVIGATE
    assert read.action.kind is ActionKind.READ

    heading = next(item for item in source.elements if item.id == "el_results_heading")
    heading = heading.model_copy(
        update={
            "id": "el_expected_heading",
            "name": heading.name.model_copy(update={"value": "Driving licence codes"}),
            "semantic_role": heading.semantic_role.model_copy(update={"value": "heading"}),
            "primary_locator": heading.primary_locator.model_copy(
                update={
                    "id": "loc_expected_heading",
                    "value": heading.primary_locator.value.model_copy(
                        update={"value": "heading:Driving licence codes"}
                    ),
                }
            ),
        }
    )
    read = read.model_copy(
        update={
            "action": read.action.model_copy(
                update={"target_element_id": heading.id, "test_data_id": None}
            )
        }
    )
    outcome = source.outcomes[0].model_copy(
        update={"related_element_ids": (heading.id,)}
    )
    page = source.pages[0].model_copy(
        update={
            "name": source.pages[0].name.model_copy(
                update={"value": "Driving licence codes"}
            ),
            "component_ids": (),
            "element_ids": (heading.id,),
        }
    )
    updated = source.model_copy(
        update={
            "process_name": source.process_name.model_copy(
                update={"value": "Driving licence codes"}
            ),
            "steps": (navigate, read),
            "outcomes": (outcome,),
            "pages": (page,),
            "components": (),
            "elements": (heading,),
            "test_data": (),
        }
    )
    return BoundedSynthesisRequest.model_validate(updated.model_dump(mode="python"))


def test_external_proposal_is_valid_without_component_or_test_data():
    request = _external_request()
    proposal = parse_pom_proposal(render_external_single_page_proposal(request))
    report = validate_pom_proposal(request, proposal)

    assert report.valid
    assert proposal.components == ()
    assert proposal.pages[0].class_name == "DrivingLicenceCodesPage"
    assert proposal.test.name == "test_driving_licence_codes"
