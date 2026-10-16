import pytest
from typer.testing import CliRunner

from mlca.cli.main import app


@pytest.mark.parametrize("status,exit_code", [("completed", 0), ("failed", 1)])
def test_cli_run_and_exit_status(tmp_path, monkeypatch, status, exit_code):
    calls = []

    def run(path, out, **kwargs):
        calls.append((path, out, kwargs))
        return {"runs": [{"status": status}]}

    monkeypatch.setattr("mlca.autonomous.runner.run", run)
    result = CliRunner().invoke(
        app,
        [
            "run",
            str(tmp_path / "input.csv"),
            "--autonomous",
            "--exclude-columns",
            "hidden",
            "--runs",
            "2",
            "--out",
            str(tmp_path / "out"),
        ],
    )
    assert result.exit_code == exit_code, result.output
    assert calls[0][2]["halt_window"] == 0
    assert calls[0][2]["window"].seconds == 0
    assert calls[0][2]["exclude_columns"] == ["hidden"]
    assert calls[0][2]["runs"] == 2


def test_cli_run_help():
    result = CliRunner().invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    for flag in ["--autonomous", "--halt-window", "--exclude-columns", "--brief", "--config"]:
        assert flag in result.output
