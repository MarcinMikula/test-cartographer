from datetime import datetime, timezone

from test_cartographer.intake.enums import IntakeAnswerAction
from test_cartographer.intake.rules import list_questions
from test_cartographer.intake.seed import MinimalContextSeed, build_minimal_context
from test_cartographer.interactive_creation.runner import (
    _ask_accept,
    _ask_candidate,
    _ask_context_summary_review,
    _ask_intake_answer,
)


def _input(values):
    iterator = iter(values)
    return lambda _prompt="": next(iterator)


def _question(question_id):
    seed = MinimalContextSeed(
        id="seed_prompt_test",
        context_id="ctx_prompt_test",
        title="Prompt test",
        initial_request="Automate catalog search.",
        created_at=datetime(2026, 8, 4, tzinfo=timezone.utc),
    )
    return next(
        item for item in list_questions(build_minimal_context(seed))
        if item.id == question_id
    )


def test_suggested_url_requires_real_enter_action() -> None:
    answer = _ask_intake_answer(
        _question("q_application_base_url"),
        suggested_value="http://127.0.0.1:1234/catalog",
        input_fn=_input([""]),
        output_fn=lambda _value: None,
    )
    assert answer.action is IntakeAnswerAction.PROVIDE
    assert answer.value == "http://127.0.0.1:1234/catalog"


def test_reserved_control_word_is_not_saved_as_context() -> None:
    messages = []
    answer = _ask_intake_answer(
        _question("q_process_purpose"),
        suggested_value=None,
        input_fn=_input(["C", "Allow visitors to find matching products."]),
        output_fn=messages.append,
    )
    assert answer.action is IntakeAnswerAction.PROVIDE
    assert answer.value == "Allow visitors to find matching products."
    assert "was not saved as context" in messages[0]


def test_context_summary_confirms_all_with_enter() -> None:
    questions = (
        _question("q_process_purpose").model_copy(update={"current_value": "Find products"}),
        _question("q_process_risk").model_copy(update={"current_value": "Hidden products"}),
    )
    decision, question, replacement = _ask_context_summary_review(
        questions,
        input_fn=_input([""]),
        output_fn=lambda _value: None,
    )
    assert decision == "confirm"
    assert question is None
    assert replacement is None


def test_context_summary_edit_rejects_control_word_as_new_value() -> None:
    messages = []
    questions = (
        _question("q_process_purpose").model_copy(update={"current_value": "Find products"}),
        _question("q_process_risk").model_copy(update={"current_value": "Hidden products"}),
    )
    decision, question, replacement = _ask_context_summary_review(
        questions,
        input_fn=_input(["EDIT", "1", "C", "Allow visitors to find matching products."]),
        output_fn=messages.append,
    )
    assert decision == "edit"
    assert question.id == "q_process_purpose"
    assert replacement == "Allow visitors to find matching products."
    assert any("was not saved as context" in message for message in messages)


def test_single_letter_review_commands_are_rejected() -> None:
    messages = []
    questions = (
        _question("q_process_purpose").model_copy(update={"current_value": "Find products"}),
    )
    decision, _, _ = _ask_context_summary_review(
        questions,
        input_fn=_input(["C", "CONFIRM"]),
        output_fn=messages.append,
    )
    assert decision == "confirm"
    assert messages == [
        "Use Enter/CONFIRM, EDIT, or QUIT. Single-letter commands are not accepted."
    ]


def test_candidate_choice_reprompts_until_allowed() -> None:
    messages = []
    selected = _ask_candidate(
        ("cand_002", "cand_003"),
        input_fn=_input(["cand_999", "cand_003"]),
        output_fn=messages.append,
    )
    assert selected == "cand_003"
    assert messages == ["Choose one of: cand_002, cand_003"]


def test_review_requires_explicit_accept_or_reject() -> None:
    messages = []
    assert _ask_accept(
        "Accept?", _input(["maybe", "a"]), messages.append
    ) is True
    assert messages == ["Enter A or R."]
