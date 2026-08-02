"""Provider-neutral synthesis adapter and deterministic replay implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from test_cartographer.synthesis.models import BoundedSynthesisRequest


class SynthesisAdapter(Protocol):
    """Minimal adapter boundary used by the bounded synthesis pipeline."""

    def execute(self, request: BoundedSynthesisRequest, prompt: str) -> str:
        """Return one raw model output string."""


@dataclass
class ReplaySynthesisAdapter:
    """Replay a stored raw output while recording the exact request and prompt."""

    raw_output: str
    last_request: BoundedSynthesisRequest | None = None
    last_prompt: str | None = None
    call_count: int = 0

    def execute(self, request: BoundedSynthesisRequest, prompt: str) -> str:
        self.last_request = request
        self.last_prompt = prompt
        self.call_count += 1
        return self.raw_output
