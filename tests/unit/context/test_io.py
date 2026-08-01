from pathlib import Path

from test_cartographer.context.io import load_context, save_context

ROOT = Path(__file__).resolve().parents[3]
VALID_FIXTURE = ROOT / "testdata" / "context" / "valid" / "public_search_flow.json"


def test_context_round_trip_is_lossless(tmp_path: Path) -> None:
    original = load_context(VALID_FIXTURE)
    target = tmp_path / "nested" / "context.json"

    save_context(original, target)
    loaded = load_context(target)

    assert loaded == original
    assert target.read_bytes().endswith(b"\n")


def test_saved_context_is_deterministic(tmp_path: Path) -> None:
    context = load_context(VALID_FIXTURE)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    save_context(context, first)
    save_context(context, second)

    assert first.read_bytes() == second.read_bytes()
