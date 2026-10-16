import json
from types import SimpleNamespace as NS

import pandas as pd

import mlca_runtime as rt
from mlca.engine.split import freeze
from mlca.paths import sha256


def test_fit_columns_are_recorded_without_values(tmp_path, monkeypatch):
    class Estimator:
        def fit(self, X):
            return self

    frame = pd.DataFrame({"measurement": [12345, 67890]}, index=[4, 8])
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    monkeypatch.setenv("MLCA_TRAIN_INDEX_SHA256", rt.index_sha256(frame.index))
    rt.fit_record(Estimator(), frame, "train")
    text = (tmp_path / "manifest.json").read_text()
    assert json.loads(text)["fits"][0]["columns"] == ["measurement"]
    assert "12345" not in text and "67890" not in text


def test_group_values_remain_in_train_for_internal_folds(tmp_path, monkeypatch):
    frame = pd.DataFrame({"group_key": [i // 3 for i in range(30)], "measurement": range(30)})
    data = tmp_path / "source.parquet"
    frame.to_parquet(data)
    monkeypatch.setattr("mlca.privacy.rows.guard", lambda *a: NS(register_split=lambda *a: None))
    monkeypatch.setattr("mlca.engine.split.seal", lambda project, key, body, path: path.write_bytes(body))
    (tmp_path / ".mlca/vault").mkdir(parents=True)
    state = NS(
        split=None,
        primary_data="sheet",
        data={"sheet": {"original_path": str(data), "sha256": sha256(data)}},
        prepared_data=None,
        task={"autonomous": True},
        template_id="clustering",
        group_column="group_key",
        project_id="fixture",
    )
    result = freeze(
        tmp_path,
        state,
        {"method": "group", "train_fraction": 0.6, "val_fraction": 0.2, "seed": 42},
        "split",
        lambda *a: None,
    )
    train = pd.read_parquet(tmp_path / result["train"]["path"])
    val = pd.read_parquet(tmp_path / result["val"]["path"])
    assert "group_key" in train
    assert not set(train.group_key) & set(val.group_key)
