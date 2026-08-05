from test_cartographer.cli import main
from test_cartographer.reactive_maintenance.io import save_maintenance_run


def test_maintenance_status_and_assessment(passed_maintenance_run, tmp_path, capsys) -> None:
    path = tmp_path / "maintenance-run.json"
    save_maintenance_run(passed_maintenance_run, path)

    assert main(["maintenance", "status", "--run", str(path)]) == 0
    status = capsys.readouterr().out
    assert "Reactive maintenance run: maintenance_run_test" in status
    assert "Failures before: 1" in status
    assert "Tests collected / passed after: 1/1" in status
    assert "Application bug claimed: false" in status

    assert main(["maintenance", "assess", "--run", str(path)]) == 0
    assessment = capsys.readouterr().out
    assert "Reactive-maintenance blockers: none" in assessment
    assert "Reactive maintenance verified: true" in assessment
    assert "Ready for controlled maintenance demonstration: true" in assessment
