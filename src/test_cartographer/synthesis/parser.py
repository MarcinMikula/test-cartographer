"""Strict raw-output parser for POM proposal schema version 0.1."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from test_cartographer.synthesis.models import PomProposal


class ProposalParseError(ValueError):
    """Protocol-level failure before substantive proposal validation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ProposalParseError(
                "duplicate_key",
                f"duplicate JSON object key: {key}",
            )
        result[key] = value
    return result


def parse_pom_proposal(raw_output: str) -> PomProposal:
    """Parse exactly one JSON object and reject protocol drift strictly."""

    stripped = raw_output.strip()
    if not stripped:
        raise ProposalParseError("empty_output", "raw output is empty")
    if "```" in stripped:
        raise ProposalParseError(
            "markdown_fence",
            "Markdown code fences are not allowed",
        )
    if not stripped.startswith("{") or not stripped.endswith("}"):
        raise ProposalParseError(
            "root_not_object",
            "raw output must contain exactly one JSON object",
        )
    try:
        payload = json.loads(stripped, object_pairs_hook=_reject_duplicate_keys)
    except ProposalParseError:
        raise
    except json.JSONDecodeError as exc:
        raise ProposalParseError(
            "invalid_json",
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc
    if not isinstance(payload, dict):
        raise ProposalParseError("root_not_object", "JSON root must be an object")
    try:
        return PomProposal.model_validate(payload)
    except ValidationError as exc:
        raise ProposalParseError(
            "schema_validation",
            f"proposal does not match schema version 0.1: {exc}",
        ) from exc
