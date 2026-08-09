from __future__ import annotations

import builtins
import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).with_name("run_sprint_14_expansion_acceptance.py")
spec = importlib.util.spec_from_file_location("s14d_runner", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def run_answers(values):
    iterator = iter(values)
    original = builtins.input
    builtins.input = lambda _prompt="": next(iterator)
    try:
        return module.ask_accept("test decision", scripted=False)
    finally:
        builtins.input = original


# A typo/control character must reprompt, not reject.
elapsed = run_answers(["\x01", "a"])
assert elapsed >= 0.0

# Normal accept remains accepted.
elapsed = run_answers(["accept"])
assert elapsed >= 0.0

# Explicit rejection remains a rejection.
try:
    run_answers(["r"])
except RuntimeError as exc:
    assert "Operator rejected" in str(exc)
else:
    raise AssertionError("Explicit R must reject.")

print("Sprint 14D.1 operator-input policy: verified")
