"""Replay and loopback-Ollama providers for discovery ambiguity questions."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Protocol

import httpx

from test_cartographer.discovery.models import DiscoveryAmbiguity, DiscoveryProfile
from test_cartographer.discovery.prompt import ambiguity_json_schema


class DiscoveryProviderError(RuntimeError):
    pass


@dataclass(frozen=True)
class DiscoveryProviderResult:
    raw_output: str
    model: str
    latency_seconds: float


class DiscoveryQuestionProvider(Protocol):
    def phrase(
        self,
        ambiguity: DiscoveryAmbiguity,
        prompt: str,
    ) -> DiscoveryProviderResult:
        ...


@dataclass
class ReplayDiscoveryProvider:
    outputs: list[str]
    model: str = "replay-discovery"
    call_count: int = 0

    def phrase(self, ambiguity, prompt) -> DiscoveryProviderResult:
        if self.call_count >= len(self.outputs):
            raise DiscoveryProviderError("no replay discovery output remains")
        output = self.outputs[self.call_count]
        self.call_count += 1
        return DiscoveryProviderResult(output, self.model, 0.0)


class OllamaDiscoveryProvider:
    def __init__(self, profile: DiscoveryProfile) -> None:
        self.profile = profile
        self._client = httpx.Client(
            base_url=profile.base_url.rstrip("/"),
            timeout=profile.timeout_seconds,
            follow_redirects=False,
            trust_env=False,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "OllamaDiscoveryProvider":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def preflight(self) -> str:
        try:
            version_response = self._client.get("/api/version")
            version_response.raise_for_status()
            version = str(version_response.json()["version"])
            tags_response = self._client.get("/api/tags")
            tags_response.raise_for_status()
            models = tags_response.json().get("models", [])
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise DiscoveryProviderError("could not reach local Ollama") from exc
        names = {
            str(value)
            for item in models
            if isinstance(item, dict)
            for value in (item.get("name"), item.get("model"))
            if value
        }
        if self.profile.model not in names:
            raise DiscoveryProviderError(
                f"local Ollama model is not installed: {self.profile.model}"
            )
        try:
            response = self._client.post(
                "/api/generate",
                json={
                    "model": self.profile.model,
                    "prompt": "",
                    "stream": False,
                    "keep_alive": self.profile.keep_alive_seconds,
                },
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise DiscoveryProviderError(
                f"local Ollama preload timed out after {self.profile.timeout_seconds:g} seconds"
            ) from exc
        except httpx.HTTPError as exc:
            raise DiscoveryProviderError("local Ollama preload failed") from exc
        return version

    def phrase(self, ambiguity, prompt) -> DiscoveryProviderResult:
        if len(prompt) > self.profile.max_prompt_characters:
            raise DiscoveryProviderError("discovery prompt exceeds configured budget")
        payload = {
            "model": self.profile.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You phrase one clarification question for bounded browser discovery. "
                        "Never select a candidate or request secrets."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "stream": False,
            "think": False,
            "keep_alive": self.profile.keep_alive_seconds,
            "format": ambiguity_json_schema(ambiguity),
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
            raise DiscoveryProviderError(
                f"local Ollama discovery request timed out after {self.profile.timeout_seconds:g} seconds"
            ) from exc
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise DiscoveryProviderError("local Ollama discovery request failed") from exc
        latency = max(0.0, time.perf_counter() - started)
        if not isinstance(raw, str) or not raw.strip():
            raise DiscoveryProviderError("local Ollama returned an empty response")
        if len(raw) > self.profile.max_response_characters:
            raise DiscoveryProviderError("discovery response exceeds configured budget")
        return DiscoveryProviderResult(
            raw_output=raw,
            model=str(body.get("model") or self.profile.model),
            latency_seconds=latency,
        )
