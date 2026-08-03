from test_cartographer.delivery.io import (
    load_application_report,
    load_code_patch,
    load_creation_evaluation,
    load_generation_profile,
    save_application_report,
    save_code_patch,
    save_creation_evaluation,
    save_generation_profile,
)


def test_delivery_contracts_round_trip(
    tmp_path,
    generation_profile,
    accepted_patch,
    application_report,
    passed_evaluation,
):
    cases = (
        (generation_profile, save_generation_profile, load_generation_profile, "profile.json"),
        (accepted_patch, save_code_patch, load_code_patch, "patch.json"),
        (application_report, save_application_report, load_application_report, "application.json"),
        (passed_evaluation, save_creation_evaluation, load_creation_evaluation, "evaluation.json"),
    )
    for model, save, load, filename in cases:
        path = tmp_path / filename
        save(model, path)
        assert load(path) == model
        assert path.read_bytes().endswith(b"\n")
