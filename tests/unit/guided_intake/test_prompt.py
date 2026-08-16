from test_cartographer.guided_intake.engine import available_questions
from test_cartographer.guided_intake.enums import GuidedIntakePhase
from test_cartographer.guided_intake.prompt import (
    build_guidance_request,
    plan_json_schema,
    render_guidance_prompt,
)


def test_prompt_contains_initial_request_and_question_ids_but_no_url_value(
    minimal_session, seed, replay_profile
) -> None:
    questions = available_questions(minimal_session)
    request = build_guidance_request(
        minimal_session.context,
        seed,
        questions,
        replay_profile,
        phase=GuidedIntakePhase.COLLECTION,
    )
    prompt = render_guidance_prompt(request)

    assert seed.initial_request in prompt
    assert "q_application_base_url" in prompt
    assert "127.0.0.1" not in prompt
    assert all(candidate.current_value is None for candidate in request.candidates)


def test_dynamic_schema_requires_exact_candidate_count(minimal_session) -> None:
    ids = tuple(question.id for question in available_questions(minimal_session))
    schema = plan_json_schema(ids, GuidedIntakePhase.COLLECTION)

    questions = schema["properties"]["questions"]
    assert questions["minItems"] == len(ids)
    assert questions["maxItems"] == len(ids)
    properties = questions["items"]["properties"]
    assert properties["question_id"]["enum"] == list(ids)
    assert properties["user_prompt"]["maxLength"] == 180
    assert properties["reason"]["maxLength"] == 240


def test_prompt_states_bounded_text_lengths(minimal_session, seed, replay_profile) -> None:
    questions = available_questions(minimal_session)
    request = build_guidance_request(
        minimal_session.context,
        seed,
        questions,
        replay_profile,
        phase=GuidedIntakePhase.COLLECTION,
    )
    prompt = render_guidance_prompt(request)

    assert "180 characters" in prompt
    assert "240 characters" in prompt

def test_review_prompt_compares_initial_request_with_current_values(
    minimal_session, seed, replay_profile
) -> None:
    questions = available_questions(minimal_session)
    request = build_guidance_request(
        minimal_session.context,
        seed,
        questions,
        replay_profile,
        phase=GuidedIntakePhase.REVIEW,
    )

    prompt = render_guidance_prompt(request)

    assert "Compare the initial request" in prompt
    assert "preserves all material initial-request intent" in prompt
    assert "Do not invent facts, criteria, constraints, or business rules" in prompt
