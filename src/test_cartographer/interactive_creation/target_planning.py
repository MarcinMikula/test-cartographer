"""Bounded LLM proposal and human authority for external discovery targets."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field as dataclass_field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Callable, Literal, Protocol

import httpx
from pydantic import Field, ValidationError, field_validator, model_validator

from test_cartographer.context.enums import ActionKind
from test_cartographer.context.models import ContractModel, ContextBundle, Identifier, NonEmptyText
from test_cartographer.discovery.models import DiscoveryTarget, RoleName
from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.interactive_creation.external import (
    build_external_public_single_page_plan,
)

_ALLOWED_ACTION_ROLES = {
    ActionKind.FILL: frozenset({"searchbox", "textbox"}),
    ActionKind.CLICK: frozenset({"button"}),
    ActionKind.SELECT: frozenset({"combobox"}),
    ActionKind.CHECK: frozenset({"checkbox"}),
    ActionKind.UNCHECK: frozenset({"checkbox"}),
    ActionKind.READ: frozenset({"generic", "heading", "list", "status", "table"}),
}
_LOCATOR_MARKERS = ("xpath", "css=", "data-testid", "get_by_", "locator(")


class ExternalTargetProposalState(StrEnum):
    BLOCKED = "blocked"
    AWAITING_REPAIR = "awaiting_repair"
    READY_FOR_REVIEW = "ready_for_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PAUSED = "paused"


class ExternalTargetDiagnosticCategory(StrEnum):
    JSON_SYNTAX = "json_syntax"
    DUPLICATE_KEY = "duplicate_key"
    SCHEMA = "schema"
    ACTION_CONTRACT = "action_contract"
    SEMANTIC_SEQUENCE = "semantic_sequence"
    UNSAFE_LOCATOR = "unsafe_locator"


class ExternalTargetProposalItem(ContractModel):
    name: NonEmptyText
    action_kind: ActionKind
    expected_roles: tuple[RoleName, ...] = Field(min_length=1, max_length=3)
    test_data_symbolic_ref: Identifier | None = None
    outcome_target: bool = False

    @field_validator("name")
    @classmethod
    def name_must_remain_semantic(cls, value: str) -> str:
        if len(value) > 160:
            raise ValueError("external target name exceeds 160 characters")
        folded = value.casefold()
        if value.startswith(("#", ".", "//", "[")) or any(
            marker in folded for marker in _LOCATOR_MARKERS
        ):
            raise ValueError("external target name must not contain a locator")
        return value

    @model_validator(mode="after")
    def validate_item(self) -> "ExternalTargetProposalItem":
        allowed_roles = _ALLOWED_ACTION_ROLES.get(self.action_kind)
        if allowed_roles is None:
            raise ValueError(
                f"unsupported external target action: {self.action_kind.value}"
            )
        if len(self.expected_roles) != len(set(self.expected_roles)):
            raise ValueError("external target roles must be unique")
        unexpected = sorted(set(self.expected_roles) - allowed_roles)
        if unexpected:
            raise ValueError(
                f"external {self.action_kind.value} target has unsupported roles: "
                f"{unexpected}"
            )
        requires_data = self.action_kind in {ActionKind.FILL, ActionKind.SELECT}
        if requires_data and self.test_data_symbolic_ref is None:
            raise ValueError("fill/select target proposal requires symbolic test data")
        if not requires_data and self.test_data_symbolic_ref is not None:
            raise ValueError("only fill/select target proposals may declare test data")
        return self


class ExternalTargetProposalPayload(ContractModel):
    schema_version: Literal["0.1"] = "0.1"
    actions: tuple[ExternalTargetProposalItem, ...] = Field(
        min_length=2,
        max_length=6,
    )

    @model_validator(mode="after")
    def validate_sequence(self) -> "ExternalTargetProposalPayload":
        _validate_semantic_sequence(self.actions)
        return self


class ExternalTargetValidationDiagnostic(ContractModel):
    category: ExternalTargetDiagnosticCategory
    path: NonEmptyText
    rule_code: Identifier
    repairable: bool

    @field_validator("path")
    @classmethod
    def path_must_be_safe(cls, value: str) -> str:
        allowed = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.$[]-"
        )
        if len(value) > 160 or any(character not in allowed for character in value):
            raise ValueError("target diagnostic path is not safe to persist")
        return value


class ExternalTargetProposalAttempt(ContractModel):
    sequence: int = Field(ge=1, le=2)
    phase: Literal["initial", "repair"]
    started_at: datetime
    completed_at: datetime
    latency_seconds: float = Field(ge=0.0)
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    prompt_characters: int = Field(ge=1)
    response_characters: int = Field(ge=1)
    valid: bool
    diagnostic: ExternalTargetValidationDiagnostic | None = None
    raw_prompt_persisted: Literal[False] = False
    raw_response_persisted: Literal[False] = False

    @field_validator("started_at", "completed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("external target attempt timestamps require offsets")
        return value

    @model_validator(mode="after")
    def validate_attempt(self) -> "ExternalTargetProposalAttempt":
        if self.completed_at < self.started_at:
            raise ValueError("proposal attempt completed_at precedes started_at")
        if self.valid == (self.diagnostic is not None):
            raise ValueError("proposal attempt validity conflicts with diagnostic")
        return self


class ExternalTargetProposalRun(ContractModel):
    schema_version: Literal["0.2"] = "0.2"
    id: Identifier
    context_id: Identifier
    provider: GuidanceProviderKind
    model: NonEmptyText
    state: ExternalTargetProposalState
    started_at: datetime
    completed_at: datetime
    reviewed_at: datetime | None = None
    latency_seconds: float = Field(ge=0.0)
    review_seconds: float = Field(default=0.0, ge=0.0)
    operator_edit_count: int = Field(default=0, ge=0)
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    response_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    prompt_characters: int = Field(ge=1)
    response_characters: int = Field(ge=1)
    attempts: tuple[ExternalTargetProposalAttempt, ...] = Field(
        min_length=1,
        max_length=2,
    )
    targets: tuple[DiscoveryTarget, ...] = Field(default=(), max_length=6)
    blocker: NonEmptyText | None = None
    diagnostic: ExternalTargetValidationDiagnostic | None = None
    repair_authorized: bool = False
    raw_prompt_persisted: Literal[False] = False
    raw_response_persisted: Literal[False] = False

    @field_validator("started_at", "completed_at", "reviewed_at")
    @classmethod
    def timestamps_must_be_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("external target proposal timestamps require offsets")
        return value

    @model_validator(mode="after")
    def validate_run(self) -> "ExternalTargetProposalRun":
        if self.completed_at < self.started_at:
            raise ValueError("proposal completed_at precedes started_at")
        sequences = tuple(item.sequence for item in self.attempts)
        phases = tuple(item.phase for item in self.attempts)
        if sequences != tuple(range(1, len(self.attempts) + 1)):
            raise ValueError("proposal attempt sequence is not contiguous")
        if phases[0] != "initial" or phases[1:] not in {(), ("repair",)}:
            raise ValueError("proposal attempts require one initial and at most one repair")
        if self.repair_authorized != (len(self.attempts) == 2):
            raise ValueError("proposal repair authority conflicts with attempts")

        latest = self.attempts[-1]
        mirrors = (
            self.completed_at == latest.completed_at,
            self.latency_seconds == latest.latency_seconds,
            self.prompt_sha256 == latest.prompt_sha256,
            self.response_sha256 == latest.response_sha256,
            self.prompt_characters == latest.prompt_characters,
            self.response_characters == latest.response_characters,
        )
        if not all(mirrors):
            raise ValueError("proposal top-level evidence must mirror latest attempt")

        if self.state is ExternalTargetProposalState.AWAITING_REPAIR:
            if self.targets or self.blocker is None or self.diagnostic is None:
                raise ValueError("repairable proposal requires diagnostic and no targets")
            if not self.diagnostic.repairable or latest.valid:
                raise ValueError("awaiting repair requires a repairable invalid attempt")
            if len(self.attempts) != 1 or self.repair_authorized:
                raise ValueError("awaiting repair must precede the one repair attempt")
            if self.reviewed_at is not None or self.review_seconds != 0.0:
                raise ValueError("awaiting repair must not contain review evidence")
            return self

        if self.state is ExternalTargetProposalState.BLOCKED:
            if self.targets or self.blocker is None or self.diagnostic is None:
                raise ValueError("blocked proposal requires diagnostic and no targets")
            if latest.valid:
                raise ValueError("blocked proposal requires an invalid latest attempt")
            if len(self.attempts) == 1 and self.diagnostic.repairable:
                raise ValueError("repairable first attempt must await operator authority")
            if self.reviewed_at is not None or self.review_seconds != 0.0:
                raise ValueError("blocked proposal must not contain review evidence")
            return self

        if self.blocker is not None or self.diagnostic is not None:
            raise ValueError("valid proposal state must not contain a diagnostic")
        if not latest.valid:
            raise ValueError("reviewable proposal requires a valid latest attempt")
        if self.state is ExternalTargetProposalState.READY_FOR_REVIEW:
            if self.reviewed_at is not None or self.review_seconds != 0.0:
                raise ValueError("pending proposal must not contain review evidence")
        elif self.reviewed_at is None:
            raise ValueError("terminal proposal state requires reviewed_at")
        _validate_semantic_sequence(self.targets)
        return self


@dataclass(frozen=True)
class ExternalTargetProviderResult:
    raw_output: str
    model: str
    latency_seconds: float


@dataclass(frozen=True)
class ExternalTargetProposalPlanningResult:
    run: ExternalTargetProposalRun
    raw_output: str = dataclass_field(repr=False)
    provider: ExternalTargetProposalProvider = dataclass_field(repr=False)


class ExternalTargetProposalProvider(Protocol):
    def propose(self, prompt: str, schema: dict) -> ExternalTargetProviderResult:
        ...


@dataclass
class ReplayExternalTargetProposalProvider:
    outputs: list[str]
    model: str = "replay-external-targets"
    call_count: int = 0
    prompts: list[str] = dataclass_field(default_factory=list, repr=False)

    def propose(self, prompt: str, schema: dict) -> ExternalTargetProviderResult:
        if self.call_count >= len(self.outputs):
            raise RuntimeError("no replay external-target output remains")
        output = self.outputs[self.call_count]
        self.call_count += 1
        self.prompts.append(prompt)
        return ExternalTargetProviderResult(
            raw_output=output,
            model=self.model,
            latency_seconds=0.0,
        )


class OllamaExternalTargetProposalProvider:
    """Request one strict semantic-action proposal from loopback Ollama."""

    def __init__(self, profile: GuidedIntakeProfile) -> None:
        self.profile = profile
        self._client = httpx.Client(
            base_url=profile.base_url.rstrip("/"),
            timeout=profile.timeout_seconds,
            follow_redirects=False,
            trust_env=False,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OllamaExternalTargetProposalProvider":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def propose(self, prompt: str, schema: dict) -> ExternalTargetProviderResult:
        if len(prompt) > self.profile.max_prompt_characters:
            raise RuntimeError("external-target prompt exceeds configured budget")
        payload = {
            "model": self.profile.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a bounded semantic UI-action planner. Propose only "
                        "reviewable actions; never selectors, locators, or facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "think": False,
            "keep_alive": self.profile.keep_alive_seconds,
            "format": schema,
            "options": {
                "temperature": self.profile.temperature,
                "seed": self.profile.seed,
                "num_predict": self.profile.max_output_tokens,
            },
        }
        started = time.perf_counter()
        try:
            response = self._client.post("/api/chat", json=payload)
            response.raise_for_status()
            body = response.json()
            raw = body["message"]["content"]
        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "local Ollama external-target request timed out after "
                f"{self.profile.timeout_seconds:g} seconds"
            ) from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise RuntimeError("local Ollama external-target request failed") from exc
        latency = max(0.0, time.perf_counter() - started)
        if not isinstance(raw, str) or not raw.strip():
            raise RuntimeError("local Ollama returned an empty target proposal")
        if len(raw) > self.profile.max_response_characters:
            raise RuntimeError("external-target response exceeds configured budget")
        return ExternalTargetProviderResult(
            raw_output=raw,
            model=str(body.get("model") or self.profile.model),
            latency_seconds=latency,
        )


def plan_external_target_proposal(
    context: ContextBundle,
    initial_request: str,
    profile: GuidedIntakeProfile,
    provider: ExternalTargetProposalProvider,
    *,
    run_id: str,
    started_at: datetime,
    completed_at_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> ExternalTargetProposalRun:
    """Compatibility wrapper returning the persisted run without ephemeral output."""
    return begin_external_target_proposal(
        context,
        initial_request,
        profile,
        provider,
        run_id=run_id,
        started_at=started_at,
        completed_at_fn=completed_at_fn,
    ).run


def begin_external_target_proposal(
    context: ContextBundle,
    initial_request: str,
    profile: GuidedIntakeProfile,
    provider: ExternalTargetProposalProvider,
    *,
    run_id: str,
    started_at: datetime,
    completed_at_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> ExternalTargetProposalPlanningResult:
    prompt = render_external_target_prompt(context, initial_request, profile)
    result = provider.propose(prompt, external_target_proposal_json_schema())
    completed_at = completed_at_fn()
    targets, blocker, diagnostic = _evaluate_target_output(
        context,
        result.raw_output,
    )
    attempt = _build_attempt(
        sequence=1,
        phase="initial",
        started_at=started_at,
        completed_at=completed_at,
        prompt=prompt,
        result=result,
        diagnostic=diagnostic,
    )
    if diagnostic is None:
        state = ExternalTargetProposalState.READY_FOR_REVIEW
    elif diagnostic.repairable:
        state = ExternalTargetProposalState.AWAITING_REPAIR
    else:
        state = ExternalTargetProposalState.BLOCKED
    run = ExternalTargetProposalRun(
        id=run_id,
        context_id=context.id,
        provider=profile.provider,
        model=result.model,
        state=state,
        started_at=started_at,
        completed_at=completed_at,
        latency_seconds=result.latency_seconds,
        prompt_sha256=attempt.prompt_sha256,
        response_sha256=attempt.response_sha256,
        prompt_characters=attempt.prompt_characters,
        response_characters=attempt.response_characters,
        attempts=(attempt,),
        targets=targets,
        blocker=blocker,
        diagnostic=diagnostic,
    )
    return ExternalTargetProposalPlanningResult(
        run=run,
        raw_output=result.raw_output,
        provider=provider,
    )


def repair_external_target_proposal(
    planning: ExternalTargetProposalPlanningResult,
    context: ContextBundle,
    initial_request: str,
    profile: GuidedIntakeProfile,
    provider: ExternalTargetProposalProvider,
    *,
    started_at: datetime,
    completed_at_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> ExternalTargetProposalPlanningResult:
    run = planning.run
    if run.state is not ExternalTargetProposalState.AWAITING_REPAIR:
        raise ValueError("external target proposal is not awaiting repair")
    if len(run.attempts) != 1 or run.repair_authorized:
        raise ValueError("external target proposal repair budget is exhausted")
    if run.diagnostic is None or not run.diagnostic.repairable:
        raise ValueError("external target proposal is not deterministically repairable")
    if provider is not planning.provider:
        raise ValueError("external target repair requires the original provider instance")

    prompt = render_external_target_repair_prompt(
        context,
        initial_request,
        profile,
        planning.raw_output,
        run.diagnostic,
    )
    result = provider.propose(prompt, external_target_proposal_json_schema())
    if result.model != run.model:
        raise RuntimeError("external target repair changed provider model")
    completed_at = completed_at_fn()
    targets, blocker, diagnostic = _evaluate_target_output(
        context,
        result.raw_output,
    )
    attempt = _build_attempt(
        sequence=2,
        phase="repair",
        started_at=started_at,
        completed_at=completed_at,
        prompt=prompt,
        result=result,
        diagnostic=diagnostic,
    )
    state = (
        ExternalTargetProposalState.READY_FOR_REVIEW
        if diagnostic is None
        else ExternalTargetProposalState.BLOCKED
    )
    updated = run.model_copy(
        update={
            "model": result.model,
            "state": state,
            "completed_at": completed_at,
            "latency_seconds": result.latency_seconds,
            "prompt_sha256": attempt.prompt_sha256,
            "response_sha256": attempt.response_sha256,
            "prompt_characters": attempt.prompt_characters,
            "response_characters": attempt.response_characters,
            "attempts": (*run.attempts, attempt),
            "targets": targets,
            "blocker": blocker,
            "diagnostic": diagnostic,
            "repair_authorized": True,
        }
    )
    validated = ExternalTargetProposalRun.model_validate(
        updated.model_dump(mode="python")
    )
    return ExternalTargetProposalPlanningResult(
        run=validated,
        raw_output=result.raw_output,
        provider=provider,
    )


def review_external_target_proposal(
    run: ExternalTargetProposalRun,
    context: ContextBundle,
    targets: tuple[DiscoveryTarget, ...],
    *,
    state: ExternalTargetProposalState,
    reviewed_at: datetime,
    review_seconds: float,
    operator_edit_count: int,
) -> ExternalTargetProposalRun:
    if state is ExternalTargetProposalState.READY_FOR_REVIEW:
        raise ValueError("review cannot retain ready_for_review state")
    if state is ExternalTargetProposalState.ACCEPTED:
        build_external_public_single_page_plan(
            context,
            plan_id="discovery_plan_external_review_validation",
            reviewed_targets=targets,
        )
    updated = run.model_copy(
        update={
            "state": state,
            "reviewed_at": reviewed_at,
            "review_seconds": review_seconds,
            "operator_edit_count": operator_edit_count,
            "targets": targets,
        }
    )
    return ExternalTargetProposalRun.model_validate(updated.model_dump(mode="python"))


def render_external_target_prompt(
    context: ContextBundle,
    initial_request: str,
    profile: GuidedIntakeProfile,
) -> str:
    allowed = set(profile.allowed_sensitivities)

    def value(item) -> str:
        if item.value is None:
            raise ValueError("external target planning requires complete process context")
        if item.sensitivity not in allowed:
            raise ValueError("external target planning context exceeds provider boundary")
        return item.value

    request = {
        "context_id": context.id,
        "initial_request": initial_request,
        "application_name": value(context.application.name),
        "environment": value(context.application.environment),
        "process_name": value(context.process.name),
        "purpose": value(context.process.purpose),
        "risk": value(context.process.risk),
        "role": value(context.process.role),
        "preconditions": [value(item) for item in context.process.preconditions],
        "expected_outcome": value(context.process.expected_outcomes[0].statement),
        "allowed_action_roles": {
            action.value: sorted(roles)
            for action, roles in _ALLOWED_ACTION_ROLES.items()
        },
    }
    instructions = {
        "role": "Plan a bounded same-page UI process for explicit human review.",
        "task": (
            "Propose two through six ordered semantic actions that preserve the "
            "accepted process context. Include at least one interaction and exactly "
            "one final READ outcome. Use symbolic non-secret references for FILL or "
            "SELECT. Do not invent selectors, locators, concrete data values, pages, "
            "counts, prices, or application facts."
        ),
        "authority": (
            "This is a proposal only. A human must review, edit, reject, or accept it "
            "before browser discovery."
        ),
        "output": "Return only JSON matching the supplied schema.",
        "request": request,
    }
    return json.dumps(
        instructions,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def render_external_target_repair_prompt(
    context: ContextBundle,
    initial_request: str,
    profile: GuidedIntakeProfile,
    invalid_raw_output: str,
    diagnostic: ExternalTargetValidationDiagnostic,
) -> str:
    if not diagnostic.repairable:
        raise ValueError("non-repairable target proposal cannot create a repair prompt")
    invalid_proposal = json.loads(
        invalid_raw_output,
        object_pairs_hook=_reject_duplicate_keys,
    )
    instructions = {
        "role": "Repair one invalid semantic UI-action proposal.",
        "task": (
            "Correct only the contract violation described by validation. Preserve "
            "the accepted process intent and do not add selectors, locators, concrete "
            "data values, pages, counts, prices, or application facts. Return only "
            "JSON matching the supplied schema."
        ),
        "authority": (
            "This is the only repair attempt. The result still requires deterministic "
            "validation and explicit human review before browser discovery."
        ),
        "validation": diagnostic.model_dump(mode="json"),
        "original_instructions": json.loads(
            render_external_target_prompt(context, initial_request, profile)
        ),
        "invalid_proposal": invalid_proposal,
    }
    return json.dumps(
        instructions,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )


def format_external_target_repair_diagnostic(
    diagnostic: ExternalTargetValidationDiagnostic,
) -> str:
    return (
        "External interaction-target proposal failed validation safely.\n"
        f"  category: {diagnostic.category.value}\n"
        f"  path: {diagnostic.path}\n"
        f"  rule: {diagnostic.rule_code}\n"
        "No provider response or input value is displayed or persisted."
    )


def read_external_target_repair_decision(*, input_fn, output_fn) -> str:
    while True:
        decision = input_fn(
            "Type RETRY for the one bounded repair attempt, or QUIT to stop: "
        ).strip().casefold()
        if decision in {"retry", "quit"}:
            return decision
        output_fn("Type RETRY or QUIT. No other repair action is supported.")


def external_target_proposal_json_schema() -> dict:
    roles = sorted({role for values in _ALLOWED_ACTION_ROLES.values() for role in values})
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["schema_version", "actions"],
        "properties": {
            "schema_version": {"const": "0.1", "type": "string"},
            "actions": {
                "type": "array",
                "minItems": 2,
                "maxItems": 6,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "name",
                        "action_kind",
                        "expected_roles",
                        "test_data_symbolic_ref",
                        "outcome_target",
                    ],
                    "properties": {
                        "name": {"type": "string", "minLength": 1, "maxLength": 160},
                        "action_kind": {
                            "type": "string",
                            "enum": [item.value for item in _ALLOWED_ACTION_ROLES],
                        },
                        "expected_roles": {
                            "type": "array",
                            "minItems": 1,
                            "maxItems": 3,
                            "uniqueItems": True,
                            "items": {"type": "string", "enum": roles},
                        },
                        "test_data_symbolic_ref": {
                            "anyOf": [
                                {
                                    "type": "string",
                                    "pattern": "^[a-z][a-z0-9_]{2,63}$",
                                },
                                {"type": "null"},
                            ]
                        },
                        "outcome_target": {"type": "boolean"},
                    },
                },
            },
        },
    }


def parse_external_target_payload(raw_output: str) -> ExternalTargetProposalPayload:
    try:
        payload = json.loads(raw_output, object_pairs_hook=_reject_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise ValueError("external target proposal is not valid JSON") from exc
    return ExternalTargetProposalPayload.model_validate(payload)


def render_replay_external_target_output(context: ContextBundle) -> str:
    outcome = context.process.expected_outcomes[0].statement.value or "Visible process result"
    payload = {
        "schema_version": "0.1",
        "actions": [
            {
                "name": "Primary process input",
                "action_kind": "fill",
                "expected_roles": ["searchbox", "textbox"],
                "test_data_symbolic_ref": "process_input",
                "outcome_target": False,
            },
            {
                "name": outcome[:160],
                "action_kind": "read",
                "expected_roles": ["generic", "list", "status"],
                "test_data_symbolic_ref": None,
                "outcome_target": True,
            },
        ],
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def format_external_target_proposal(targets) -> str:
    lines = [
        "Review the proposed semantic actions. No locator or selector is authorized.",
    ]
    for index, target in enumerate(targets, start=1):
        data = target.test_data_symbolic_ref or "—"
        roles = ", ".join(target.expected_roles)
        outcome = " | FINAL OUTCOME" if target.outcome_target else ""
        lines.append(
            f"  {index}. {target.action_kind.value.upper()} | {target.name} | "
            f"roles={roles} | data={data}{outcome}"
        )
    return "\n".join(lines)


def review_target_proposal_interactively(
    context,
    targets,
    *,
    input_fn,
    output_fn,
):
    working = _validate_candidate(context, tuple(targets))
    edits = 0
    while True:
        output_fn(format_external_target_proposal(working))
        command = input_fn(
            "Press Enter to ACCEPT, or type EDIT, ADD, REMOVE, REJECT, or QUIT: "
        ).strip().casefold()
        if command in {"", "accept"}:
            return "accepted", _validate_candidate(context, working), edits
        if command == "reject":
            return "rejected", working, edits
        if command == "quit":
            return "paused", working, edits
        if command == "add":
            if len(working) >= 6:
                output_fn("The proposal already contains the maximum six actions.")
                continue
            try:
                action = _read_action(input_fn=input_fn, output_fn=output_fn)
            except ValueError as exc:
                output_fn(f"Added action is invalid: {exc}")
                continue
            if action is None:
                continue
            candidate = (*working[:-1], action, working[-1])
        elif command == "remove":
            if len(working) <= 2:
                output_fn("A rich proposal must retain at least two actions.")
                continue
            selected = _read_number(
                len(working) - 1,
                input_fn=input_fn,
                output_fn=output_fn,
            )
            if selected is None:
                continue
            candidate = tuple(
                item
                for index, item in enumerate(working, start=1)
                if index != selected
            )
        elif command == "edit":
            selected = _read_number(
                len(working),
                input_fn=input_fn,
                output_fn=output_fn,
            )
            if selected is None:
                continue
            index = selected - 1
            field = _read_choice(
                "Field NAME, KIND, ROLES, or DATA (or CANCEL): ",
                {"name", "kind", "roles", "data"},
                input_fn=input_fn,
                output_fn=output_fn,
            )
            if field is None:
                continue
            current = working[index]
            updates = {}
            if field == "name":
                value = _read_text(
                    "Semantic name (or CANCEL): ",
                    input_fn=input_fn,
                    output_fn=output_fn,
                )
                if value is None:
                    continue
                updates["name"] = value
            elif field == "kind":
                if index == len(working) - 1:
                    output_fn("The final action must remain READ.")
                    continue
                kind = _read_choice(
                    "Action FILL, CLICK, SELECT, CHECK, or UNCHECK (or CANCEL): ",
                    {"fill", "click", "select", "check", "uncheck"},
                    input_fn=input_fn,
                    output_fn=output_fn,
                )
                if kind is None:
                    continue
                action_kind = ActionKind(kind)
                updates["action_kind"] = action_kind
                roles = _read_roles(input_fn=input_fn, output_fn=output_fn)
                if roles is None:
                    continue
                updates["expected_roles"] = roles
                updates["test_data_symbolic_ref"] = (
                    _read_text(
                        "Symbolic non-secret data reference (or CANCEL): ",
                        input_fn=input_fn,
                        output_fn=output_fn,
                    )
                    if action_kind in {ActionKind.FILL, ActionKind.SELECT}
                    else None
                )
                if (
                    action_kind in {ActionKind.FILL, ActionKind.SELECT}
                    and updates["test_data_symbolic_ref"] is None
                ):
                    continue
            elif field == "roles":
                roles = _read_roles(input_fn=input_fn, output_fn=output_fn)
                if roles is None:
                    continue
                updates["expected_roles"] = roles
            else:
                if current.action_kind not in {ActionKind.FILL, ActionKind.SELECT}:
                    output_fn("Only FILL and SELECT actions use symbolic test data.")
                    continue
                data = _read_text(
                    "Symbolic non-secret data reference (or CANCEL): ",
                    input_fn=input_fn,
                    output_fn=output_fn,
                )
                if data is None:
                    continue
                updates["test_data_symbolic_ref"] = data.casefold()
            value = current.model_copy(update=updates).model_dump(mode="python")
            if value.get("test_data_symbolic_ref") is not None:
                value["test_data_symbolic_ref"] = value[
                    "test_data_symbolic_ref"
                ].casefold()
            try:
                edited = DiscoveryTarget.model_validate(value)
            except ValueError as exc:
                output_fn(f"Edited action is invalid: {exc}")
                continue
            candidate_list = list(working)
            candidate_list[index] = edited
            candidate = tuple(candidate_list)
        else:
            output_fn("Use Enter/ACCEPT, EDIT, ADD, REMOVE, REJECT, or QUIT.")
            continue

        try:
            working = _validate_candidate(context, candidate)
        except ValueError as exc:
            output_fn(f"Change rejected by the target contract: {exc}")
            continue
        edits += 1


def save_external_target_proposal_run(
    run: ExternalTargetProposalRun,
    path: str | Path,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"{run.model_dump_json(indent=2, exclude_none=False)}\n",
        encoding="utf-8",
        newline="\n",
    )


def _read_action(*, input_fn, output_fn):
    kind = _read_choice(
        "Action FILL, CLICK, SELECT, CHECK, or UNCHECK (or CANCEL): ",
        {"fill", "click", "select", "check", "uncheck"},
        input_fn=input_fn,
        output_fn=output_fn,
    )
    if kind is None:
        return None
    name = _read_text(
        "Semantic name (or CANCEL): ",
        input_fn=input_fn,
        output_fn=output_fn,
    )
    if name is None:
        return None
    roles = _read_roles(input_fn=input_fn, output_fn=output_fn)
    if roles is None:
        return None
    action_kind = ActionKind(kind)
    data = None
    if action_kind in {ActionKind.FILL, ActionKind.SELECT}:
        data = _read_text(
            "Symbolic non-secret data reference (or CANCEL): ",
            input_fn=input_fn,
            output_fn=output_fn,
        )
        if data is None:
            return None
        data = data.casefold()
    return DiscoveryTarget(
        id="target_pending",
        element_id="el_pending",
        owner_id="page_pending",
        name=name,
        action_kind=action_kind,
        expected_roles=roles,
        test_data_symbolic_ref=data,
    )


def _validate_candidate(context, targets):
    page_id = context.pages[0].id
    normalized = []
    for index, target in enumerate(targets, start=1):
        value = target.model_dump(mode="python")
        value.update(
            {
                "id": f"target_reviewed_{index:02d}",
                "element_id": f"el_reviewed_{index:02d}",
                "owner_id": page_id,
                "outcome_target": index == len(targets),
            }
        )
        normalized.append(DiscoveryTarget.model_validate(value))
    result = tuple(normalized)
    _validate_semantic_sequence(result)
    build_external_public_single_page_plan(
        context,
        plan_id="discovery_plan_external_operator_validation",
        reviewed_targets=result,
    )
    return result


def _validate_semantic_sequence(items) -> None:
    if not 2 <= len(items) <= 6:
        raise ValueError("external target proposal requires two through six actions")
    if not any(item.action_kind is not ActionKind.READ for item in items):
        raise ValueError("external target proposal requires at least one interaction")
    reads = [item for item in items if item.action_kind is ActionKind.READ]
    outcomes = [item for item in items if item.outcome_target]
    if reads != [items[-1]] or outcomes != [items[-1]]:
        raise ValueError("external target proposal requires one final READ outcome")
    refs = [
        item.test_data_symbolic_ref
        for item in items
        if item.test_data_symbolic_ref is not None
    ]
    if len(refs) != len(set(refs)):
        raise ValueError("external target proposal symbolic references must be unique")
    for item in items:
        ExternalTargetProposalItem(
            name=item.name,
            action_kind=item.action_kind,
            expected_roles=item.expected_roles,
            test_data_symbolic_ref=item.test_data_symbolic_ref,
            outcome_target=item.outcome_target,
        )


def _read_number(maximum, *, input_fn, output_fn):
    while True:
        raw = input_fn(
            f"Select action number 1-{maximum}, or type CANCEL: "
        ).strip()
        if raw.casefold() == "cancel":
            return None
        if raw.isdigit() and 1 <= int(raw) <= maximum:
            return int(raw)
        output_fn(f"Enter a number from 1 to {maximum}, or CANCEL.")


def _read_choice(prompt, choices, *, input_fn, output_fn):
    while True:
        raw = input_fn(prompt).strip().casefold()
        if raw == "cancel":
            return None
        if raw in choices:
            return raw
        output_fn(f"Choose one of: {', '.join(sorted(choices))}, or CANCEL.")


def _read_text(prompt, *, input_fn, output_fn):
    while True:
        raw = input_fn(prompt).strip()
        if raw.casefold() == "cancel":
            return None
        if raw:
            return raw
        output_fn("Enter a non-empty value, or CANCEL.")


def _read_roles(*, input_fn, output_fn):
    while True:
        raw = input_fn(
            "Semantic roles separated by commas (or CANCEL): "
        ).strip()
        if raw.casefold() == "cancel":
            return None
        roles = tuple(
            dict.fromkeys(
                value.strip().casefold()
                for value in raw.split(",")
                if value.strip()
            )
        )
        if roles:
            return roles
        output_fn("Enter at least one semantic role, or CANCEL.")


def _reject_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key in target proposal: {key}")
        value[key] = item
    return value


@dataclass(frozen=True)
class _ExternalTargetEvaluation:
    targets: tuple[DiscoveryTarget, ...]
    blocker: str | None
    diagnostic: ExternalTargetValidationDiagnostic | None


def _evaluate_target_output(
    context: ContextBundle,
    raw_output: str,
) -> tuple[
    tuple[DiscoveryTarget, ...],
    str | None,
    ExternalTargetValidationDiagnostic | None,
]:
    try:
        payload = parse_external_target_payload(raw_output)
        page_id = context.pages[0].id
        targets = tuple(
            DiscoveryTarget(
                id=f"target_reviewed_{index:02d}",
                element_id=f"el_reviewed_{index:02d}",
                owner_id=page_id,
                name=item.name,
                action_kind=item.action_kind,
                expected_roles=item.expected_roles,
                test_data_symbolic_ref=item.test_data_symbolic_ref,
                outcome_target=item.outcome_target,
            )
            for index, item in enumerate(payload.actions, start=1)
        )
        build_external_public_single_page_plan(
            context,
            plan_id="discovery_plan_external_proposal_validation",
            reviewed_targets=targets,
        )
    except ValueError as exc:
        blocker = _blocker_code(exc)
        return (), blocker, _safe_validation_diagnostic(exc, blocker)
    return targets, None, None


def _build_attempt(
    *,
    sequence: int,
    phase: Literal["initial", "repair"],
    started_at: datetime,
    completed_at: datetime,
    prompt: str,
    result: ExternalTargetProviderResult,
    diagnostic: ExternalTargetValidationDiagnostic | None,
) -> ExternalTargetProposalAttempt:
    return ExternalTargetProposalAttempt(
        sequence=sequence,
        phase=phase,
        started_at=started_at,
        completed_at=completed_at,
        latency_seconds=result.latency_seconds,
        prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        response_sha256=hashlib.sha256(
            result.raw_output.encode("utf-8")
        ).hexdigest(),
        prompt_characters=len(prompt),
        response_characters=len(result.raw_output),
        valid=diagnostic is None,
        diagnostic=diagnostic,
    )


def _safe_validation_diagnostic(
    error: ValueError,
    blocker: str,
) -> ExternalTargetValidationDiagnostic:
    error_type = ""
    location: tuple[object, ...] = ()
    if isinstance(error, ValidationError):
        errors = error.errors(include_input=False, include_url=False)
        if errors:
            error_type = str(errors[0].get("type") or "")
            location = tuple(errors[0].get("loc") or ())

    known = {
        "invalid_json": (
            ExternalTargetDiagnosticCategory.JSON_SYNTAX,
            "json_parse",
            False,
        ),
        "duplicate_json_key": (
            ExternalTargetDiagnosticCategory.DUPLICATE_KEY,
            "unique_json_key",
            False,
        ),
        "locator_like_name": (
            ExternalTargetDiagnosticCategory.UNSAFE_LOCATOR,
            "semantic_name_only",
            False,
        ),
        "invalid_final_read": (
            ExternalTargetDiagnosticCategory.SEMANTIC_SEQUENCE,
            "final_read_outcome",
            True,
        ),
        "missing_interaction": (
            ExternalTargetDiagnosticCategory.SEMANTIC_SEQUENCE,
            "interaction_required",
            True,
        ),
        "invalid_action_count": (
            ExternalTargetDiagnosticCategory.SEMANTIC_SEQUENCE,
            "action_count",
            True,
        ),
        "invalid_action_role": (
            ExternalTargetDiagnosticCategory.ACTION_CONTRACT,
            "action_role_allowlist",
            True,
        ),
        "invalid_symbolic_data": (
            ExternalTargetDiagnosticCategory.ACTION_CONTRACT,
            "symbolic_data_contract",
            True,
        ),
    }
    if blocker in known:
        category, rule_code, repairable = known[blocker]
    else:
        rules = {
            "missing": "required_field",
            "extra_forbidden": "no_extra_fields",
            "literal_error": "literal_value",
            "enum": "enum_value",
            "too_short": "minimum_items",
            "too_long": "maximum_items",
            "string_pattern_mismatch": "identifier_pattern",
            "string_too_short": "minimum_length",
            "string_too_long": "maximum_length",
            "string_type": "string_type",
            "bool_type": "boolean_type",
            "list_type": "array_type",
        }
        category = ExternalTargetDiagnosticCategory.SCHEMA
        if error_type in rules:
            rule_code = rules[error_type]
            repairable = True
        else:
            rule_code = "unsupported_validation_rule"
            repairable = False

    path = _safe_validation_path(location, blocker)
    return ExternalTargetValidationDiagnostic(
        category=category,
        path=path,
        rule_code=rule_code,
        repairable=repairable,
    )


def _safe_validation_path(location: tuple[object, ...], blocker: str) -> str:
    if location:
        parts = []
        for item in location:
            if isinstance(item, int):
                if not parts:
                    parts.append("$")
                parts[-1] = f"{parts[-1]}[{item}]"
                continue
            value = str(item)
            if not value.replace("_", "").isalnum():
                return "$"
            parts.append(value)
        return ".".join(parts)
    fallbacks = {
        "invalid_final_read": "actions[-1]",
        "missing_interaction": "actions",
        "invalid_action_count": "actions",
        "invalid_symbolic_data": "actions",
        "invalid_action_role": "actions",
    }
    return fallbacks.get(blocker, "$")


def _blocker_code(error: ValueError) -> str:
    message = str(error).casefold()
    categories = (
        ("valid json", "invalid_json"),
        ("duplicate json key", "duplicate_json_key"),
        ("final read outcome", "invalid_final_read"),
        ("at least one interaction", "missing_interaction"),
        ("two through six actions", "invalid_action_count"),
        ("unsupported roles", "invalid_action_role"),
        ("symbolic", "invalid_symbolic_data"),
        ("locator", "locator_like_name"),
    )
    for fragment, code in categories:
        if fragment in message:
            return code
    return "invalid_target_contract"
