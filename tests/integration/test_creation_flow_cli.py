from test_cartographer.cli import main
from test_cartographer.creation_flow.io import save_creation_flow_run


def test_creation_status_and_assessment(tmp_path, passed_creation_run, capsys) -> None:
    target = tmp_path / "run.json"
    save_creation_flow_run(passed_creation_run, target)

    assert main(["creation", "status", "--run", str(target)]) == 0
    status = capsys.readouterr().out
    assert "Creation flow: creation_flow_test" in status
    assert "Live LLM calls: 3" in status
    assert "Measured savings claimed: false" in status

    assert main(["creation", "assess", "--run", str(target)]) == 0
    assessment = capsys.readouterr().out
    assert "Creation mechanics blockers: none" in assessment
    assert "Creation mechanics verified: true" in assessment
    assert "Ready for human-trigger integration: true" in assessment
    assert "External user-demo blockers: interactive_human_trigger_missing" in assessment
    assert "Ready for external user demonstration: false" in assessment
