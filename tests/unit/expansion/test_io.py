from test_cartographer.expansion.assessment import assess_expansion_run
from test_cartographer.expansion.io import (
    load_expansion_assessment,
    load_expansion_plan,
    load_expansion_request,
    load_expansion_run,
    save_expansion_assessment,
    save_expansion_plan,
    save_expansion_request,
    save_expansion_run,
)


def test_expansion_contracts_round_trip(
    tmp_path,
    expansion_request,
    accepted_expansion_plan,
    passed_fixture_run,
):
    run = passed_fixture_run
    assessment = assess_expansion_run(run)
    artefacts = (
        (expansion_request, save_expansion_request, load_expansion_request, "request.json"),
        (accepted_expansion_plan, save_expansion_plan, load_expansion_plan, "plan.json"),
        (run, save_expansion_run, load_expansion_run, "run.json"),
        (assessment, save_expansion_assessment, load_expansion_assessment, "assessment.json"),
    )
    for expected, saver, loader, name in artefacts:
        path = tmp_path / name
        saver(expected, path)
        assert loader(path) == expected
        assert path.read_bytes().endswith(b"\n")


def test_saved_expansion_run_contains_no_raw_page_or_secret_values(tmp_path, passed_fixture_run):
    run = passed_fixture_run
    path = tmp_path / "run.json"
    save_expansion_run(run, path)
    rendered = path.read_text(encoding="utf-8")
    assert "raw_page" in rendered
    assert '"raw_page_persisted": false' in rendered
    assert "password" not in rendered.casefold()
