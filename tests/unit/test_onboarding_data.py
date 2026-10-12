import pytest

from mlca.errors import MlcaUserError
from mlca.log.replay import replay
from mlca.log.store import Store
from mlca.project.discovery import discover, registrations
from mlca.project.init import column_for, initialise, study_ready


def test_folder_discovery_and_duplicate_stems(tmp_path):
    for folder in ["a", "b", ".git", ".mlca"]:
        (tmp_path / folder).mkdir()
        (tmp_path / folder / "data.csv").write_text("x,y\n1,0\n")
    (tmp_path / "ignore.xlsx").write_text("not supported")
    (tmp_path / "link.csv").symlink_to(tmp_path / "a/data.csv")
    found = discover([tmp_path])
    assert found == [tmp_path / "a/data.csv", tmp_path / "b/data.csv"]
    assert [n for n, p in registrations(found)] == ["data", "data_2"]
    assert discover([found[0], found[0]]) == [found[0]]
    with pytest.raises(MlcaUserError, match="symlink"):
        discover([tmp_path / "link.csv"])


def test_empty_and_unsupported(tmp_path):
    with pytest.raises(MlcaUserError, match="No supported"):
        discover([tmp_path])
    with pytest.raises(MlcaUserError, match="supported table"):
        discover([tmp_path / "missing.csv"])


def test_deferred_columns_and_primary(tmp_path, monkeypatch):
    monkeypatch.setattr("mlca.project.init.create", lambda *_: {"lock_sha256": "stub", "packages": []})
    folder = tmp_path / "data"
    folder.mkdir()
    (folder / "first.csv").write_text("a,b\n1,2\n")
    (folder / "second.csv").write_text("x,y\n1,0\n2,1\n")
    with pytest.raises(MlcaUserError, match="main study table"):
        initialise(tmp_path / "missing", [folder], "tabular_classification", {})
    root = initialise(tmp_path / "p", [folder], "tabular_classification", {}, primary_data="second")
    state = replay(Store(root).read())
    assert state.primary_data == "second"
    assert state.columns == {"target": None}
    assert not study_ready(state)[0]
    with pytest.raises(MlcaUserError, match="Unresolved"):
        column_for(state)
    state.columns = {"target": "y"}
    state.brief["unit"] = "one patient"
    assert study_ready(state)[0]
    assert column_for(state) == "y"


def test_old_single_table_primary_fallback(tmp_path):
    from mlca.log.schema import ProjectState

    state = ProjectState(
        data={"table": {}}, inventory=[{"name": "table", "columns": ["y"]}], brief={"target": "y"}
    )
    assert column_for(state) == "y"


def test_split_uses_selected_main_not_first(tmp_path, monkeypatch):
    import pandas as pd

    from mlca.api import Session
    from mlca.engine.split import freeze
    from mlca.runner.run_step import inputs_for
    from mlca.templates.model import ActionSpec

    monkeypatch.setattr("mlca.project.init.create", lambda *_: {"lock_sha256": "stub", "packages": []})
    folder = tmp_path / "data"
    folder.mkdir()
    (folder / "a_support.csv").write_text("note\n1\n")
    pd.DataFrame({"x": range(100), "y": [0, 1] * 50}).to_csv(folder / "z_main.csv", index=False)
    root = initialise(
        tmp_path / "p",
        [folder],
        "tabular_classification",
        {"target": "y", "unit": "sample"},
        primary_data="z_main",
    )
    with Session.open(root) as session:
        action = ActionSpec(
            id="audit", event="onboard", title="Audit", prompt="", inputs=[{"ref": "registered_data"}]
        )
        assert next(iter(inputs_for(action, session.state, root))) == "z_main"
        result = freeze(
            root,
            session.state,
            {"method": "stratified", "train_fraction": 0.6, "val_fraction": 0.2, "seed": 42},
            "selected-main",
            session.emit,
        )
        assert result["primary_data"] == "z_main"
        assert sum(result["counts"].values()) == 100
        assert list(pd.read_parquet(root / result["train"]["path"]).columns) == ["x", "y"]
        assert session.state.split["primary_data"] == "z_main"
