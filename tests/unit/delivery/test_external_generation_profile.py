from pathlib import Path

from test_cartographer.delivery.io import load_generation_profile

ROOT = Path(__file__).resolve().parents[3]


def test_external_generation_profile_requires_no_invented_test_data():
    profile = load_generation_profile(
        ROOT / "profiles/delivery/external_public_single_page.json"
    )

    assert profile.test_data_bindings == ()
    assert profile.environment_url_variable == "TEST_CARTOGRAPHER_TARGET_URL"
    assert profile.secret_values_included is False
