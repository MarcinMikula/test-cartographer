from pathlib import Path

import pytest

from test_cartographer.interactive_creation.runner import (
    InteractiveFlowStopped,
    run_human_triggered_creation_flow,
)


class _StopAfterStartup(RuntimeError):
    pass


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def test_existing_output_stops_before_mutation_or_browser(
    tmp_path,
    interactive_profile,
):
    output = tmp_path / "existing-run"
    output.mkdir()
    sentinel = output / "immutable-evidence.bin"
    sentinel.write_bytes(b"immutable evidence\x00\xff")
    sentinel_before = sentinel.read_bytes()
    browser_calls = []

    def browser_opener(*args, **kwargs):
        browser_calls.append((args, kwargs))
        raise AssertionError("browser must not start after output collision")

    def unexpected_input(_prompt=""):
        raise AssertionError(
            "operator input must not start after output collision"
        )

    with pytest.raises(
        InteractiveFlowStopped,
        match="output directory already exists; choose a new run id",
    ):
        run_human_triggered_creation_flow(
            project_root=_repo_root(),
            output_dir=output,
            framework_root=None,
            interactive_profile=interactive_profile,
            ollama_base_url="http://127.0.0.1:11434",
            ollama_model="qwen2.5-coder:7b",
            timeout_seconds=1.0,
            provider_mode="replay",
            browser_opener=browser_opener,
            input_fn=unexpected_input,
        )

    assert sentinel.read_bytes() == sentinel_before
    assert browser_calls == []
    assert {item.name for item in output.iterdir()} == {
        "immutable-evidence.bin"
    }


def test_fresh_output_is_created_before_first_operator_input(
    tmp_path,
    interactive_profile,
):
    output = tmp_path / "fresh-run"
    browser_calls = []

    def browser_opener(*args, **kwargs):
        browser_calls.append((args, kwargs))
        raise AssertionError("browser must not start before intake")

    def stop_at_first_input(_prompt=""):
        raise _StopAfterStartup("first operator input reached")

    with pytest.raises(_StopAfterStartup, match="first operator input reached"):
        run_human_triggered_creation_flow(
            project_root=_repo_root(),
            output_dir=output,
            framework_root=None,
            interactive_profile=interactive_profile,
            ollama_base_url="http://127.0.0.1:11434",
            ollama_model="qwen2.5-coder:7b",
            timeout_seconds=1.0,
            provider_mode="replay",
            browser_opener=browser_opener,
            input_fn=stop_at_first_input,
            output_fn=lambda _message: None,
        )

    assert output.is_dir()
    assert (output / "operator-session.json").is_file()
    assert browser_calls == []
