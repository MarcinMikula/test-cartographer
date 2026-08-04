import json

import httpx
import pytest

from test_cartographer.discovery.enums import DiscoveryProviderKind
from test_cartographer.discovery.models import DiscoveryAmbiguity, DiscoveryProfile
from test_cartographer.discovery.provider import DiscoveryProviderError, OllamaDiscoveryProvider


def _profile() -> DiscoveryProfile:
    return DiscoveryProfile(
        id="discovery_live_test",
        provider=DiscoveryProviderKind.OLLAMA,
        model="qwen2.5-coder:7b",
        base_url="http://127.0.0.1:11434",
        timeout_seconds=10.0,
        max_output_tokens=256,
        keep_alive_seconds=900,
    )


def test_provider_preloads_and_sends_bounded_chat_payload() -> None:
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/version":
            return httpx.Response(200, json={"version": "test"})
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": [{"name": "qwen2.5-coder:7b"}]})
        if request.url.path == "/api/generate":
            return httpx.Response(200, json={"done": True})
        if request.url.path == "/api/chat":
            return httpx.Response(
                200,
                json={
                    "model": "qwen2.5-coder:7b",
                    "message": {
                        "content": json.dumps(
                            {
                                "schema_version": "0.1",
                                "ambiguity_id": "amb_target_search_submit",
                                "candidate_ids": ["cand_002", "cand_003"],
                                "user_prompt": "Which candidate submits the form?",
                                "reason": "Both candidates have equal semantic evidence.",
                            }
                        )
                    },
                },
            )
        raise AssertionError(request.url)

    provider = OllamaDiscoveryProvider(_profile())
    provider._client.close()
    provider._client = httpx.Client(
        base_url="http://127.0.0.1:11434",
        transport=httpx.MockTransport(handler),
    )
    ambiguity = DiscoveryAmbiguity(
        id="amb_target_search_submit",
        target_id="target_search_submit",
        candidate_ids=("cand_002", "cand_003"),
    )
    try:
        assert provider.preflight() == "test"
        result = provider.phrase(ambiguity, "bounded prompt")
    finally:
        provider.close()
    assert result.model == "qwen2.5-coder:7b"
    generate_payload = json.loads(next(r for r in requests if r.url.path == "/api/generate").content)
    chat_payload = json.loads(next(r for r in requests if r.url.path == "/api/chat").content)
    assert generate_payload["keep_alive"] == 900
    assert chat_payload["stream"] is False
    assert chat_payload["think"] is False
    assert chat_payload["keep_alive"] == 900
    assert chat_payload["options"]["num_predict"] == 256
    assert chat_payload["format"]["properties"]["candidate_ids"]["items"]["enum"] == [
        "cand_002",
        "cand_003",
    ]


def test_provider_reports_timeout(monkeypatch) -> None:
    provider = OllamaDiscoveryProvider(_profile())

    def fail(*args, **kwargs):
        raise httpx.ReadTimeout("slow")

    monkeypatch.setattr(provider._client, "post", fail)
    ambiguity = DiscoveryAmbiguity(
        id="amb_target_search_submit",
        target_id="target_search_submit",
        candidate_ids=("cand_002", "cand_003"),
    )
    try:
        with pytest.raises(DiscoveryProviderError, match="timed out"):
            provider.phrase(ambiguity, "bounded prompt")
    finally:
        provider.close()
