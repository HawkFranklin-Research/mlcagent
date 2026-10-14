import json

import numpy as np
import pytest

import mlca_runtime as runtime


def test_save_json_supports_nested_numpy_scalars(tmp_path, monkeypatch):
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    output = runtime.save_json(
        {"count": np.int64(3), "nested": [np.bool_(True), np.float32(1.5)]}, "summary.json"
    )
    assert json.loads(output.read_text()) == {"count": 3, "nested": [True, 1.5]}


def test_manifest_fact_supports_numpy_scalar(tmp_path, monkeypatch):
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    runtime.record_fact_candidate("rows", np.int64(9), source="summary.json")
    assert json.loads((tmp_path / "manifest.json").read_text())["facts"][0]["value"] == 9


@pytest.mark.parametrize("value", [float("nan"), np.float32("nan"), np.float64("inf")])
def test_json_still_rejects_nonfinite_numbers(tmp_path, monkeypatch, value):
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    with pytest.raises(ValueError):
        runtime.save_json({"value": value}, "summary.json")


def test_json_still_rejects_arbitrary_objects(tmp_path, monkeypatch):
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    with pytest.raises(TypeError):
        runtime.save_json({"value": object()}, "summary.json")


def test_named_inputs_report_safe_repairable_key_errors(tmp_path, monkeypatch):
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    (tmp_path / "inputs.json").write_text(json.dumps({"train": {"path": str(tmp_path / "train.parquet")}}))
    declared = runtime.inputs()
    assert declared["train"] == tmp_path / "train.parquet"
    assert declared.get("missing") is None
    with pytest.raises(KeyError) as caught:
        declared["private-example-identifier"]
    assert str(caught.value).startswith("MLCA:")
    assert "private-example-identifier" not in str(caught.value)
    from mlca.runner.run_step import diagnostics

    message = diagnostics({"stderr": "mlca_runtime.InputKeyError: " + str(caught.value)}, False)
    assert "filenames are not keys" in message
