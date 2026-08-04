"""Replay and local Ollama providers for guided interview planning."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Protocol

import httpx

from test_cartographer.guided_intake.models import GuidanceRequest, GuidedIntakeProfile
from test_cartographer.guided_intake.prompt import plan_json_schema


class GuidanceProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class GuidanceProviderResult:
    raw_output: str
    model: str
    latency_seconds: float


class GuidanceProvider(Protocol):
    def plan(self, request: GuidanceRequest, prompt: str) -> GuidanceProviderResult:
        ...


@dataclass
class ReplayGuidanceProvider:
    outputs: list[str]
    model: str = "replay-guidance"
    call_count: int = 0

    def plan(self, request: GuidanceRequest, prompt: str) -> GuidanceProviderResult:
        if self.call_count >= len(self.outputs):
            raise GuidanceProviderError("no replay guidance output remains")
        output = self.outputs[self.call_count]
        self.call_count += 1
        return GuidanceProviderResult(
            raw_output=output,
            model=self.model,
            latency_seconds=0.0,
        )


class OllamaGuidanceProvider:
    """Use only the loopback Ollama API with structured output enabled."""

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

    def __enter__(self) -> "OllamaGuidanceProvider":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def preflight(self) -> str:
        try:
            version_response = self._client.get("/api/version")
            version_response.raise_for_status()
            version = str(version_response.json()["version"])
            models_response = self._client.get("/api/tags")
            models_response.raise_for_status()
            models = models_response.json().get("models", [])
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise GuidanceProviderError(
                "could not reach the local Ollama API or parse its response"
            ) from exc
        names = {
            str(value)
            for item in models
            if isinstance(item, dict)
            for value in (item.get("name"), item.get("model"))
            if value
        }
        if self.profile.model not in names:
            raise GuidanceProviderError(
                f"local Ollama model is not installed: {self.profile.model}"
            )
        try:
            preload_response = self._client.post(
                "/api/generate",
                json={
                    "model": self.profile.model,
                    "prompt": "",
                    "stream": False,
                    "keep_alive": self.profile.keep_alive_seconds,
                },
            )
            preload_response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise GuidanceProviderError(
                "local Ollama model preload timed out after "
                f"{self.profile.timeout_seconds:g} seconds"
            ) from exc
        except httpx.HTTPError as exc:
            raise GuidanceProviderError("local Ollama model preload failed") from exc
        return version

    def plan(self, request: GuidanceRequest, prompt: str) -> GuidanceProviderResult:
        if len(prompt) > self.profile.max_prompt_characters:
            raise GuidanceProviderError("guided prompt exceeds configured character budget")
        schema = plan_json_schema(
            tuple(candidate.question_id for candidate in request.candidates),
            request.phase,
        )
        payload = {
            "model": self.profile.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a bounded interview planner for test automation. "
                        "You select and rephrase supplied questions only."
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
            raise GuidanceProviderError(
                "local Ollama guided request timed out after "
                f"{self.profile.timeout_seconds:g} seconds"
            ) from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise GuidanceProviderError("local Ollama guided request failed") from exc
        latency = max(0.0, time.perf_counter() - started)
        if not isinstance(raw, str) or not raw.strip():
            raise GuidanceProviderError("local Ollama returned an empty guided response")
        if len(raw) > self.profile.max_response_characters:
            raise GuidanceProviderError("guided response exceeds configured character budget")
        return GuidanceProviderResult(
            raw_output=raw,
            model=str(body.get("model") or self.profile.model),
            latency_seconds=latency,
        )
