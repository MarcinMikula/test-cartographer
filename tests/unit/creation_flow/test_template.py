from pathlib import Path

from test_cartographer.creation_flow.template import render_reference_pom_proposal
from test_cartographer.synthesis.io import load_synthesis_request
from test_cartographer.synthesis.parser import parse_pom_proposal
from test_cartographer.synthesis.validation import validate_pom_proposal

ROOT = Path(__file__).resolve().parents[3]


def test_reference_template_traverses_existing_protocol() -> None:
    request = load_synthesis_request(ROOT / "testdata/synthesis/request/public_search.json")
    proposal = parse_pom_proposal(render_reference_pom_proposal(request))
    report = validate_pom_proposal(request, proposal)

    assert report.valid
    assert proposal.request_id == request.id
    assert proposal.context_id == request.context_id
    assert proposal.pages[0].class_name == "CatalogPage"
    assert proposal.components[0].class_name == "CatalogSearchForm"
    assert proposal.claim_flags.business_correctness is False
