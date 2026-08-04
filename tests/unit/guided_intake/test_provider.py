import json

import httpx
import pytest

from test_cartographer.guided_intake.engine import available_questions
from test_cartographer.guided_intake.enums import GuidedIntakePhase
from test_cartographer.guided_intake.models import GuidedIntakeProfile
from test_cartographer.guided_intake.prompt import build_guidance_request, render_guidance_prompt
from test_cartographer.guided_intake.provider import (
    GuidanceProviderError,
    OllamaGuidanceProvider,
)

from .conftest import render_plan


def test_ollama_provider_uses_local_structured_chat(
    minimal_session, seed, replay_profile
) -> None:
    profile = GuidedIntakeProfile(
        id="guided_test_ollama",
        provider="ollama",
        model="qwen2.5-coder:7b",
        base_url="http://127.0.0.1:11434",
    )
    questions = available_questions(minimal_session)
    request = build_guidance_request(
        minimal_session.context,
        seed,
        questions,
        profile,
        phase=GuidedIntakePhase.COLLECTION,
    )
    prompt = render_guidance_prompt(request)
    seen = {}

    def handler(http_request: httpx.Request) -> httpx.Response:
        if http_request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "test"})
        if http_request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={"models": [{"name": "qwen2.5-coder:7b"}]},
            )
        payload = json.loads(http_request.content)
        if http_request.url.path == "/api/generate":
            seen["preload"] = payload
            return httpx.Response(200, json={"done": True})
        seen.update(payload)
        return httpx.Response(
            200,
            json={
                "model": "qwen2.5-coder:7b",
                "message": {
                    "role": "assistant",
                    "content": render_plan(
                        "collection", [question.id for question in questions]
                    ),
                },
                "done": True,
            },
        )

    provider = OllamaGuidanceProvider(profile)
    provider._client.close()
    provider._client = httpx.Client(
        base_url=profile.base_url,
        transport=httpx.MockTransport(handler),
        trust_env=False,
    )
    try:
        assert provider.preflight() == "test"
        result = provider.plan(request, prompt)
    finally:
        provider.close()

    assert result.model == "qwen2.5-coder:7b"
    assert seen["preload"] == {
        "model": "qwen2.5-coder:7b",
        "prompt": "",
        "stream": False,
        "keep_alive": 900,
    }
    assert seen["stream"] is False
    assert seen["think"] is False
    assert seen["keep_alive"] == 900
    assert isinstance(seen["format"], dict)
    assert seen["options"] == {
        "temperature": 0.0,
        "seed": 42,
        "num_predict": 768,
    }


def test_ollama_provider_reports_configured_timeout(
    minimal_session, seed
) -> None:
    profile = GuidedIntakeProfile(
        id="guided_timeout_ollama",
        provider="ollama",
        model="qwen2.5-coder:7b",
        base_url="http://127.0.0.1:11434",
        timeout_seconds=600.0,
    )
    questions = available_questions(minimal_session)
    request = build_guidance_request(
        minimal_session.context,
        seed,
        questions,
        profile,
        phase=GuidedIntakePhase.COLLECTION,
    )
    prompt = render_guidance_prompt(request)

    def handler(http_request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=http_request)

    provider = OllamaGuidanceProvider(profile)
    provider._client.close()
    provider._client = httpx.Client(
        base_url=profile.base_url,
        transport=httpx.MockTransport(handler),
        trust_env=False,
    )
    try:
        with pytest.raises(
            GuidanceProviderError,
            match=r"timed out after 600 seconds",
        ):
            provider.plan(request, prompt)
    finally:
        provider.close()


def test_ollama_preflight_reports_preload_timeout() -> None:
    profile = GuidedIntakeProfile(
        id="guided_preload_timeout",
        provider="ollama",
        model="qwen2.5-coder:7b",
        base_url="http://127.0.0.1:11434",
        timeout_seconds=600.0,
    )

    def handler(http_request: httpx.Request) -> httpx.Response:
        if http_request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "test"})
        if http_request.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={"models": [{"name": "qwen2.5-coder:7b"}]},
            )
        raise httpx.ReadTimeout("timed out", request=http_request)

    provider = OllamaGuidanceProvider(profile)
    provider._client.close()
    provider._client = httpx.Client(
        base_url=profile.base_url,
        transport=httpx.MockTransport(handler),
        trust_env=False,
    )
    try:
        with pytest.raises(
            GuidanceProviderError,
            match=r"preload timed out after 600 seconds",
        ):
            provider.preflight()
    finally:
        provider.close()
