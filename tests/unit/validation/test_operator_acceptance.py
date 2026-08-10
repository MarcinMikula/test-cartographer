import pytest

from test_cartographer.validation.operator_acceptance import (
    compute_working_tree_fingerprint,
)


def test_working_tree_fingerprint_is_order_independent(tmp_path):
    (tmp_path / "a.txt").write_text("a\n", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b\n", encoding="utf-8")
    assert compute_working_tree_fingerprint(
        tmp_path, ("b.txt", "a.txt")
    ) == compute_working_tree_fingerprint(tmp_path, ("a.txt", "b.txt"))


def test_working_tree_fingerprint_changes_with_content(tmp_path):
    path = tmp_path / "a.txt"
    path.write_text("a\n", encoding="utf-8")
    first = compute_working_tree_fingerprint(tmp_path, ("a.txt",))
    path.write_text("changed\n", encoding="utf-8")
    assert compute_working_tree_fingerprint(tmp_path, ("a.txt",)) != first


def test_working_tree_fingerprint_rejects_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        compute_working_tree_fingerprint(tmp_path, ("missing.txt",))

def test_ask_choice_counts_invalid_reprompt(monkeypatch):
    import builtins

    from test_cartographer.validation.operator_acceptance import _ask_choice

    answers = iter(["d", "h"])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    value, _elapsed, invalid = _ask_choice(
        "Difficulty: ",
        {"h": "hard"},
    )

    assert value == "hard"
    assert invalid == 1

