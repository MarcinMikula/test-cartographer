"""Strict parser for one structured guided-interview plan."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from test_cartographer.guided_intake.models import GuidedInterviewPlan


class GuidanceParseError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise GuidanceParseError("duplicate_key", f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_guided_plan(raw_output: str) -> GuidedInterviewPlan:
    stripped = raw_output.strip()
    if not stripped:
        raise GuidanceParseError("empty_output", "guided output is empty")
    if "```" in stripped:
        raise GuidanceParseError("markdown_fence", "Markdown fences are not allowed")
    if not stripped.startswith("{") or not stripped.endswith("}"):
        raise GuidanceParseError("root_not_object", "output must be one JSON object")
    try:
        payload = json.loads(stripped, object_pairs_hook=_reject_duplicate_keys)
    except GuidanceParseError:
        raise
    except json.JSONDecodeError as exc:
        raise GuidanceParseError(
            "invalid_json",
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        ) from exc
    try:
        return GuidedInterviewPlan.model_validate(payload)
    except ValidationError as exc:
        raise GuidanceParseError(
            "schema_validation", f"guided plan does not match schema 0.1: {exc}"
        ) from exc
