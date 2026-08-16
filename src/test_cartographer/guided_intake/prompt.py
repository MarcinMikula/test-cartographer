"""Minimized deterministic prompt construction for guided intake."""

from __future__ import annotations

import json

from test_cartographer.context.models import ContextBundle, KnowledgeText
from test_cartographer.guided_intake.enums import GuidedIntakePhase
from test_cartographer.guided_intake.models import (
    GuidanceCandidate,
    GuidanceKnownField,
    GuidanceRequest,
    GuidedIntakeProfile,
)
from test_cartographer.intake.models import IntakeQuestion
from test_cartographer.intake.seed import MinimalContextSeed

_USER_PROMPT_MAX_CHARACTERS = 180
_REASON_MAX_CHARACTERS = 240

_PROHIBITED = (
    "Do not answer the questions on the user's behalf.",
    "Do not request passwords, tokens, cookies, personal data, or secret values.",
    "Do not invent question IDs, application facts, selectors, pages, or outcomes.",
    "Return every supplied question exactly once.",
)


def build_guidance_request(
    context: ContextBundle,
    seed: MinimalContextSeed,
    questions: tuple[IntakeQuestion, ...],
    profile: GuidedIntakeProfile,
    *,
    phase: GuidedIntakePhase,
) -> GuidanceRequest:
    allowed = set(profile.allowed_sensitivities)
    known: list[GuidanceKnownField] = []
    values = (
        ("application.name", context.application.name),
        ("application.environment", context.application.environment),
        ("process.name", context.process.name),
        ("process.purpose", context.process.purpose),
        ("process.risk", context.process.risk),
        ("process.role", context.process.role),
    )
    for path, value in values:
        known.append(
            GuidanceKnownField(
                path=path,
                status=value.status.value,
                value=(
                    value.value
                    if value.value is not None and value.sensitivity in allowed
                    else None
                ),
            )
        )

    candidates: list[GuidanceCandidate] = []
    for question in questions:
        safe_current = None
        if (
            question.target_path != "application.base_url"
            and question.current_value is not None
            and question.sensitivity in allowed
        ):
            safe_current = question.current_value
        candidates.append(
            GuidanceCandidate(
                question_id=question.id,
                kind=question.kind,
                base_prompt=question.prompt,
                target_path=question.target_path,
                current_value=safe_current,
            )
        )

    initial_request = (
        seed.initial_request
        if seed.sensitivity in allowed
        else "A human requested a new UI automation process."
    )
    return GuidanceRequest(
        phase=phase,
        context_id=context.id,
        initial_request=initial_request,
        known_fields=tuple(known),
        candidates=tuple(candidates),
        prohibited_requests=_PROHIBITED,
    )


def render_guidance_prompt(request: GuidanceRequest) -> str:
    payload = request.model_dump(mode="json")
    if request.phase is GuidedIntakePhase.COLLECTION:
        task = (
            "Order all candidate questions and rephrase each for the human operator. "
            "Collection questions require an answer, so do not use the confirmation "
            "answer shape. Do not answer any question."
        )
    else:
        task = (
            "Compare the initial request with every candidate's current value. Use "
            "the confirmation answer shape only when that value preserves all material "
            "initial-request intent relevant to its target and needs no clarification. "
            "Otherwise ask one targeted clarification and use short_phrase, sentence, "
            "or bullets. Do not invent facts, criteria, constraints, or business rules."
        )
    instructions = {
        "role": "Plan a concise human interview for software-test automation discovery.",
        "task": (
            f"{task} Keep each user_prompt at or below "
            f"{_USER_PROMPT_MAX_CHARACTERS} characters and each reason at or below "
            f"{_REASON_MAX_CHARACTERS} characters."
        ),
        "output": "Return only JSON matching the supplied schema.",
        "request": payload,
    }
    return json.dumps(instructions, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def plan_json_schema(question_ids: tuple[str, ...], phase: GuidedIntakePhase) -> dict:
    count = len(question_ids)
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "phase", "questions"],
        "properties": {
            "schema_version": {"const": "0.1", "type": "string"},
            "phase": {"const": phase.value, "type": "string"},
            "questions": {
                "type": "array",
                "minItems": count,
                "maxItems": count,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["question_id", "user_prompt", "reason", "answer_shape"],
                    "properties": {
                        "question_id": {"type": "string", "enum": list(question_ids)},
                        "user_prompt": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": _USER_PROMPT_MAX_CHARACTERS,
                        },
                        "reason": {
                            "type": "string",
                            "minLength": 1,
                            "maxLength": _REASON_MAX_CHARACTERS,
                        },
                        "answer_shape": {
                            "type": "string",
                            "enum": ["short_phrase", "sentence", "bullets", "confirmation"],
                        },
                    },
                },
            },
        },
    }
