import pytest
from typer.testing import CliRunner

from mlca.cli.main import app
from mlca.errors import MlcaUserError
from mlca.log.replay import replay
from mlca.log.schema import ProjectState
from mlca.log.store import Store
from mlca.project.init import column_for, initialise, resolve_column, resolve_columns


def test_exact_case_and_ambiguity():
    assert resolve_column("Y", ["x", "y"], "target") == "y"
    assert resolve_column("y", ["y", "Y"], "target") == "y"
    with pytest.raises(MlcaUserError, match="Available columns: y, Y"):
        resolve_column("yY", ["y", "Y"], "target")
    assert resolve_column("the y column", ["y"], "target", lambda *_: "y") == "y"


def test_init_structured_columns(tmp_path, monkeypatch):
    monkeypatch.setattr("mlca.project.init.create", lambda *_: {"lock_sha256": "stub", "packages": []})
    data = tmp_path / "table.csv"
    data.write_text("x,y\n1,0\n2,1\n")
    root = initialise(tmp_path / "p", [data], "tabular_classification", {"target": "Y"})
    state = replay(Store(root).read())
    assert state.brief["target"] == "Y"
    assert state.columns == {"target": "y"}
    with pytest.raises(MlcaUserError, match="Available columns: x, y"):
        initialise(tmp_path / "bad", [data], "tabular_classification", {"target": "the y column"})
    assert not (tmp_path / "bad/.mlca").exists()


def test_noninteractive_cli_lists_columns(tmp_path):
    data = tmp_path / "d.csv"
    data.write_text("x,y\n1,0\n")
    brief = tmp_path / "brief.yaml"
    brief.write_text("target: the y column\n")
    # The public entry point formats MlcaUserError; CliRunner exposes it directly.
    result = CliRunner().invoke(
        app, ["init", str(tmp_path / "p"), "--data", str(data), "--brief-file", str(brief)]
    )
    assert isinstance(result.exception, MlcaUserError)
    assert "Available columns: x, y" in str(result.exception)


def test_survival_columns_and_old_projects():
    inventory = [{"columns": ["duration", "observed"]}]
    columns = resolve_columns({"target": "DURATION", "event_column": "Observed"}, inventory, "survival")
    assert columns == {"target": "duration", "duration": "duration", "event_column": "observed"}
    state = ProjectState(inventory=inventory, brief={"target": "duration"})
    assert column_for(state) == "duration"
    state.brief["target"] = "the duration column"
    with pytest.raises(MlcaUserError, match="Unresolved target column"):
        column_for(state)


def test_interactive_cli_picks_column(tmp_path, monkeypatch):
    monkeypatch.setattr("mlca.project.init.create", lambda *_: {"lock_sha256": "stub", "packages": []})
    data = tmp_path / "data.csv"
    data.write_text("x,y\n1,0\n2,1\n")
    root = tmp_path / "project"
    result = CliRunner().invoke(
        app, ["init", str(root), "--data", str(data)], input="classify\nthe y column\none row\ny\n"
    )
    assert result.exit_code == 0, result.output
    assert "Available columns for target: x, y" in result.output
    state = replay(Store(root).read())
    assert state.brief["target"] == "the y column"
    assert state.columns["target"] == "y"
