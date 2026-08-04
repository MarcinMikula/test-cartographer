from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.context.readiness import assess_readiness
from test_cartographer.intake.rules import list_questions
from test_cartographer.intake.seed import build_minimal_context


def test_minimal_seed_builds_valid_unknown_heavy_context(seed) -> None:
    context = build_minimal_context(seed)

    assert context.application.name.status is KnowledgeStatus.UNKNOWN
    assert context.application.base_url.value is None
    assert context.process.purpose.value is None
    assert context.process.steps[0].intent.value == seed.initial_request
    assert context.process.steps[0].expected_state.value is None
    assert len(context.evidence) == 1
    assert context.evidence[0].summary == "A human supplied the initial automation request."


def test_minimal_context_exposes_all_human_seed_gaps(seed) -> None:
    context = build_minimal_context(seed)

    assert [question.id for question in list_questions(context)] == [
        "q_application_name",
        "q_application_environment",
        "q_application_base_url",
        "q_process_name",
        "q_process_purpose",
        "q_process_risk",
        "q_process_role",
        "q_precondition_1",
        "q_outcome_outcome_target",
    ]
    assert assess_readiness(context).ready is False
