from test_cartographer.expansion.assessment import assess_expansion_run
from test_cartographer.expansion.enums import ExpansionRunStatus
from test_cartographer.expansion.models import ExpansionRun


def test_real_operator_run_is_ready_for_controlled_demo(passed_real_run):
    assessment = assess_expansion_run(passed_real_run)
    assert assessment.blockers == ()
    assert assessment.expansion_verified is True
    assert assessment.controlled_demo_ready is True


def test_fixture_run_verifies_mechanics_but_not_real_operator_demo(passed_fixture_run):
    assessment = assess_expansion_run(passed_fixture_run)
    assert assessment.blockers == ()
    assert assessment.expansion_verified is True
    assert assessment.controlled_demo_ready is False


def test_nonpassed_run_is_not_verified(passed_fixture_run):
    run = passed_fixture_run
    payload = run.model_dump(mode="python")
    payload.update(
        status=ExpansionRunStatus.PENDING,
        finished_at=None,
        synthesis_run_id=None,
        adaptation_plan_id=None,
        code_patch_id=None,
        application_report_id=None,
        target_test=None,
    )
    pending = ExpansionRun.model_validate(payload)
    assessment = assess_expansion_run(pending)
    assert assessment.expansion_verified is False
    assert "run did not finish in passed state" in assessment.blockers
