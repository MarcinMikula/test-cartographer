from test_cartographer.interactive_creation.io import (
    load_interactive_profile,
    load_operator_session,
    save_interactive_profile,
    save_operator_session,
)


def test_interactive_contracts_round_trip(
    tmp_path, interactive_profile, operator_session
) -> None:
    profile_path = tmp_path / "profile.json"
    session_path = tmp_path / "session.json"
    save_interactive_profile(interactive_profile, profile_path)
    save_operator_session(operator_session, session_path)
    assert load_interactive_profile(profile_path) == interactive_profile
    assert load_operator_session(session_path) == operator_session
