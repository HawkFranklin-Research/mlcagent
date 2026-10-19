"""Regression tests for the fixes after the second acceptance batch (B-0032 to B-0035, L-0011, L-0012)."""

import json
import sqlite3
from types import SimpleNamespace as NS

import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer, StandardScaler

import mlca_runtime as rt
from mlca.autonomous.runner import setup_reason
from mlca.paths import resource
from mlca.rails import load
from mlca.runner.run_step import INTERPRET_ROWS, interpretation_sample, source_columns


def test_binary_recoding_of_a_grade_is_not_a_label_hierarchy():
    rails = load(resource("rails"))
    text = rails.instructions("navigator", "onboard", "binary")
    assert "hierarchy of named categories" in text and "thresholds or recodes an ordinal grade" in text
    later = rails.instructions("worker", "interpret", "multiclass")
    assert "do not require it to be a Pipeline" in later


@pytest.fixture
def step(tmp_path, monkeypatch):
    (tmp_path / "outputs").mkdir()
    (tmp_path / "source_columns.json").write_text(json.dumps(["day", "temp"]))
    pd.DataFrame({"day": range(300), "temp": [float(i % 7) for i in range(300)]}).to_parquet(
        tmp_path / "train.parquet"
    )
    (tmp_path / "inputs.json").write_text(json.dumps({"train": {"path": str(tmp_path / "train.parquet")}}))
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    monkeypatch.setenv("MLCA_SOURCE_COLUMNS", str(tmp_path / "source_columns.json"))
    return monkeypatch


@pytest.mark.parametrize("event", ["preprocess", "model"])
def test_saved_objects_must_accept_raw_columns(step, event):
    step.setenv("MLCA_EVENT", event)
    derived = StandardScaler().fit(pd.DataFrame({"temp": [1.0, 2.0], "day_month": [1, 2]}))
    with pytest.raises(rt.FitRuleError, match=r"^MLCA: .*\['day_month'\]"):
        rt.save_model(derived, "preprocessor.pkl")
    rt.save_model(StandardScaler().fit(pd.DataFrame({"temp": [1.0, 2.0]})), "preprocessor.pkl")


def test_selectors_after_preprocessing_are_not_checked(step):
    step.setenv("MLCA_EVENT", "features")
    rt.save_model(StandardScaler().fit(pd.DataFrame({"num__temp": [1.0, 2.0]})), "selector.pkl")


def test_interpretation_reads_a_fixed_ordered_sample_of_large_partitions(tmp_path):
    large = tmp_path / "val.parquet"
    pd.DataFrame({"x": range(INTERPRET_ROWS + 500)}, index=range(5, INTERPRET_ROWS + 505)).to_parquet(large)
    first = interpretation_sample(tmp_path, "val", large, "a" * 64)
    frame = pd.read_parquet(first)
    assert len(frame) == INTERPRET_ROWS and frame.index.is_monotonic_increasing
    assert interpretation_sample(tmp_path, "val", large, "a" * 64) == first
    small = tmp_path / "train.parquet"
    pd.DataFrame({"x": range(10)}).to_parquet(small)
    assert interpretation_sample(tmp_path, "train", small, "b" * 64) == small


def test_source_columns_exclude_the_stored_index(tmp_path):
    pd.DataFrame({"a": [1], "b": [2]}, index=[7]).to_parquet(tmp_path / "train.parquet", index=True)
    state = NS(split={"train": {"path": "train.parquet"}})
    assert source_columns(state, tmp_path) == ["a", "b"]
    assert source_columns(NS(split=None), tmp_path) is None


def test_setup_reason_keeps_database_and_disk_causes():
    assert setup_reason(sqlite3.OperationalError("database or disk is full")) == "database or disk is full"
    assert setup_reason(OSError(28, "No space left on device", "/private/path")) == "No space left on device"
    assert setup_reason(ValueError("row value 3.2")) == ""


def test_saved_objects_must_keep_the_row_index_on_later_rows(step):
    # Fitting on rows indexed from 0 hides a component that drops the index (Bike Sharing, batch-10).
    step.setenv("MLCA_EVENT", "preprocess")
    train = pd.read_parquet(rt.inputs()["train"])
    dropping = ColumnTransformer(
        [
            ("num", StandardScaler(), ["temp"]),
            ("day", FunctionTransformer(lambda X: X.reset_index(drop=True)), ["day"]),
        ]
    ).set_output(transform="pandas")
    dropping.fit(train)
    with pytest.raises(rt.FitRuleError, match="^MLCA: Saved object .*row index"):
        rt.save_model(dropping, "preprocessor.pkl")
    kept = ColumnTransformer([("num", StandardScaler(), ["temp", "day"])]).set_output(transform="pandas")
    rt.save_model(kept.fit(train), "preprocessor.pkl")


def test_clustering_and_representation_are_separated_by_feature_kind():
    text = load(resource("rails")).instructions("navigator", "onboard", "clustering")
    assert "channels of one signal" in text and "distinct measured attributes" in text
