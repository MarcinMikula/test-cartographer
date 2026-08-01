from pathlib import Path

from test_cartographer.context.enums import KnowledgeStatus
from test_cartographer.context.io import load_context
from test_cartographer.context.models import ContextBundle, KnowledgeText
from test_cartographer.intake.rules import assess_intake, list_questions

ROOT = Path(__file__).resolve().parents[3]


def _context(state: str) -> ContextBundle:
    return load_context(ROOT / "testdata" / "context" / state / "public_search_flow.json")


def test_incomplete_context_has_stable_human_question_order() -> None:
    questions = list_questions(_context("incomplete"))

    assert [question.id for question in questions] == [
        "q_process_risk",
        "q_outcome_outcome_matching_results",
        "q_open_question_expected_matching_rule",
    ]


def test_browser_only_locator_issue_does_not_create_intake_question() -> None:
    questions = list_questions(_context("incomplete"))

    assert all("locator" not in question.target_path for question in questions)


def test_intake_assessment_filters_full_readiness_to_human_issues() -> None:
    report = assess_intake(_context("incomplete"))
    codes = {issue.code for issue in report.issues}

    assert report.complete is False
    assert report.blocker_count == 3
    assert codes == {
        "risk_not_confirmed",
        "outcome_not_confirmed",
        "blocking_question_open",
    }


def test_valid_context_has_no_intake_questions() -> None:
    context = _context("valid")

    assert list_questions(context) == ()
    assert assess_intake(context).complete is True


def test_unresolved_conflict_is_asked_before_business_fields() -> None:
    questions = list_questions(_context("conflicting"))

    assert questions[0].kind.value == "conflict_resolution"
    assert questions[0].target_path.startswith("conflicts.")


def test_supported_but_unconfirmed_value_enters_review_queue() -> None:
    context = _context("valid")
    provided_risk = KnowledgeText(
        value=context.process.risk.value,
        status=KnowledgeStatus.PROVIDED,
        evidence_ids=context.process.risk.evidence_ids,
        sensitivity=context.process.risk.sensitivity,
    )
    process = context.process.model_copy(update={"risk": provided_risk})
    candidate = context.model_copy(update={"process": process})
    updated = ContextBundle.model_validate(candidate.model_dump(mode="python"))

    report = assess_intake(updated)

    questions = list_questions(updated)

    assert [question.id for question in questions] == ["q_process_risk"]
    assert questions[0].current_value == provided_risk.value
    assert report.complete is True
    assert report.warning_count == 1
    assert report.issues[0].code == "risk_not_confirmed"


def test_review_questions_appear_only_after_required_collection_is_resolved() -> None:
    context = _context("incomplete")
    risk = KnowledgeText(
        value="Search failures hide relevant items.",
        status=KnowledgeStatus.PROVIDED,
        evidence_ids=("ev_human_scope",),
        sensitivity=context.process.risk.sensitivity,
    )
    outcome = context.process.expected_outcomes[0].model_copy(
        update={
            "statement": KnowledgeText(
                value="Matching items are visible.",
                status=KnowledgeStatus.PROVIDED,
                evidence_ids=("ev_human_scope",),
                sensitivity=context.process.expected_outcomes[0].statement.sensitivity,
            )
        }
    )
    process = context.process.model_copy(
        update={"risk": risk, "expected_outcomes": (outcome,)}
    )
    candidate = context.model_copy(
        update={"process": process, "open_questions": ()}
    )
    updated = ContextBundle.model_validate(candidate.model_dump(mode="python"))

    assert [question.id for question in list_questions(updated)] == [
        "q_process_risk",
        "q_outcome_outcome_matching_results",
    ]
