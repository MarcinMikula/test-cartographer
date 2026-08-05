from test_cartographer.interactive_creation.assessment import assess_interactive_creation


def test_real_operator_session_reaches_external_demo_readiness(
    operator_session, interactive_creation_run, interactive_profile
) -> None:
    report = assess_interactive_creation(
        operator_session, interactive_creation_run, interactive_profile
    )
    assert report.human_trigger_verified is True
    assert report.external_user_demo_ready is True
    assert report.blockers == ()


def test_fixture_creation_run_does_not_reach_interactive_readiness(
    operator_session, passed_creation_run, interactive_profile
) -> None:
    report = assess_interactive_creation(
        operator_session, passed_creation_run, interactive_profile
    )
    assert report.human_trigger_verified is False
    assert report.external_user_demo_ready is False
    assert "creation_run_not_marked_interactive" in report.blockers
    assert "creation_run_still_fixture_assisted" in report.blockers


def test_missing_synthesis_handoff_confirmation_blocks_readiness(
    operator_session, interactive_creation_run, interactive_profile
) -> None:
    session_without_handoff = operator_session.model_copy(
        update={
            "actions": tuple(
                action
                for action in operator_session.actions
                if action.kind.value != "synthesis_handoff_confirmation"
            )
        }
    )
    report = assess_interactive_creation(
        session_without_handoff, interactive_creation_run, interactive_profile
    )
    assert report.human_trigger_verified is False
    assert "synthesis_handoff_confirmation_missing" in report.blockers


def test_missing_execution_trigger_blocks_readiness(
    operator_session, interactive_creation_run, interactive_profile
) -> None:
    session_without_execution = operator_session.model_copy(
        update={
            "actions": tuple(
                action
                for action in operator_session.actions
                if action.kind.value != "execution_trigger"
            )
        }
    )
    report = assess_interactive_creation(
        session_without_execution, interactive_creation_run, interactive_profile
    )
    assert report.human_trigger_verified is False
    assert "real_execution_trigger_missing" in report.blockers
