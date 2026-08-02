"""Bounded synthesis pipeline with exact request and raw-output preservation."""

from __future__ import annotations

import hashlib
from datetime import datetime

from test_cartographer.synthesis.adapter import SynthesisAdapter
from test_cartographer.synthesis.enums import SynthesisRunStatus
from test_cartographer.synthesis.models import (
    BoundedSynthesisRequest,
    ProposalParseFailure,
    SynthesisRun,
)
from test_cartographer.synthesis.parser import ProposalParseError, parse_pom_proposal
from test_cartographer.synthesis.request import render_synthesis_prompt
from test_cartographer.synthesis.validation import validate_pom_proposal


def run_synthesis(
    request: BoundedSynthesisRequest,
    adapter: SynthesisAdapter,
    *,
    run_id: str,
    started_at: datetime,
    completed_at: datetime,
) -> SynthesisRun:
    """Execute one adapter call and preserve protocol versus validation failure."""

    prompt = render_synthesis_prompt(request)
    raw_output = adapter.execute(request, prompt)
    prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    try:
        proposal = parse_pom_proposal(raw_output)
    except ProposalParseError as exc:
        return SynthesisRun(
            id=run_id,
            request=request,
            prompt_sha256=prompt_sha256,
            raw_output=raw_output,
            status=SynthesisRunStatus.PROTOCOL_ERROR,
            parse_failure=ProposalParseFailure(code=exc.code, message=exc.message),
            started_at=started_at,
            completed_at=completed_at,
        )

    validation = validate_pom_proposal(request, proposal)
    status = (
        SynthesisRunStatus.READY_FOR_REVIEW
        if validation.valid
        else SynthesisRunStatus.VALIDATION_REJECTED
    )
    return SynthesisRun(
        id=run_id,
        request=request,
        prompt_sha256=prompt_sha256,
        raw_output=raw_output,
        status=status,
        proposal=proposal,
        validation=validation,
        started_at=started_at,
        completed_at=completed_at,
    )
