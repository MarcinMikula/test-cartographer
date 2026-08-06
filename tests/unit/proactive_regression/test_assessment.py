from test_cartographer.proactive_regression.assessment import assess_proactive_regression_run


def test_passed_real_run_is_controlled_demo_ready(passed_run) -> None:
    report = assess_proactive_regression_run(passed_run)
    assert report.blockers == ()
    assert report.proactive_regression_verified is True
    assert report.controlled_demo_ready is True


def test_scripted_run_verifies_mechanics_but_not_real_operator_demo(passed_run) -> None:
    scripted = passed_run.model_copy(
        update={
            "interactive_human_trigger_used": False,
            "fixture_decisions_used": True,
            "headed_browser_used": False,
        }
    )
    report = assess_proactive_regression_run(scripted)
    assert report.proactive_regression_verified is True
    assert report.controlled_demo_ready is False
