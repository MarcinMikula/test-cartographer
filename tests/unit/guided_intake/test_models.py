from datetime import datetime, timezone

import pytest

from test_cartographer.guided_intake.enums import GuidanceProviderKind
from test_cartographer.guided_intake.models import GuidedIntakeProfile


def test_ollama_profile_requires_loopback_http() -> None:
    with pytest.raises(ValueError, match="local HTTP"):
        GuidedIntakeProfile(
            id="guided_remote",
            provider=GuidanceProviderKind.OLLAMA,
            model="qwen2.5-coder:7b",
            base_url="https://example.com",
        )


def test_ollama_profile_rejects_cloud_model_name() -> None:
    with pytest.raises(ValueError, match="cloud model"):
        GuidedIntakeProfile(
            id="guided_cloud",
            provider=GuidanceProviderKind.OLLAMA,
            model="gpt-oss:120b-cloud",
            base_url="http://127.0.0.1:11434",
        )


def test_replay_profile_does_not_require_http(replay_profile) -> None:
    assert replay_profile.provider is GuidanceProviderKind.REPLAY
    assert replay_profile.base_url == "replay://local"


def test_ollama_profile_requires_api_root_url() -> None:
    with pytest.raises(ValueError, match="local API root"):
        GuidedIntakeProfile(
            id="guided_nested_api",
            provider=GuidanceProviderKind.OLLAMA,
            model="qwen2.5-coder:7b",
            base_url="http://127.0.0.1:11434/api",
        )


def test_ollama_profile_bounds_generation_budget() -> None:
    with pytest.raises(ValueError):
        GuidedIntakeProfile(
            id="guided_unbounded_output",
            provider=GuidanceProviderKind.OLLAMA,
            model="qwen2.5-coder:7b",
            base_url="http://127.0.0.1:11434",
            max_output_tokens=4096,
        )

    with pytest.raises(ValueError):
        GuidedIntakeProfile(
            id="guided_unbounded_keepalive",
            provider=GuidanceProviderKind.OLLAMA,
            model="qwen2.5-coder:7b",
            base_url="http://127.0.0.1:11434",
            keep_alive_seconds=7200,
        )
