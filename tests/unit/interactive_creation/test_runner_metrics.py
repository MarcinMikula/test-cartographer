from types import SimpleNamespace

from test_cartographer.interactive_creation.runner import (
    _discovery_live_llm_call_count,
)


def test_discovery_live_llm_calls_zero_without_guidance_turns() -> None:
    run = SimpleNamespace(guidance_turns=())

    assert _discovery_live_llm_call_count(run) == 0


def test_discovery_live_llm_calls_one_for_one_guidance_turn() -> None:
    run = SimpleNamespace(guidance_turns=(object(),))

    assert _discovery_live_llm_call_count(run) == 1


def test_discovery_live_llm_calls_counts_multiple_turns_exactly() -> None:
    run = SimpleNamespace(guidance_turns=(object(), object(), object()))

    assert _discovery_live_llm_call_count(run) == 3
