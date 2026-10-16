import json
from types import SimpleNamespace as NS

import pandas as pd
import pytest

import mlca_runtime
from mlca.engine.checks import evaluate
from mlca.roles.worker import runtime_api
from mlca.runner.run_step import diagnostics
from mlca.task_metrics import default_metric
from mlca.templates.registry import get


@pytest.mark.parametrize(
    "template",
    [
        "tabular_classification",
        "multilabel_classification",
        "regression",
        "clustering",
        "representation",
        "survival",
    ],
)
@pytest.mark.parametrize("event,partition", [("validation", "val"), ("test", "test")])
def test_prediction_audit_contract_matches_runtime(tmp_path, monkeypatch, template, event, partition):
    action = get(template).actions["audit_" + event]
    output = action.outputs[0]
    assert output.kind == "data" and output.name.endswith(".parquet")
    assert "save_row_outputs" in action.prompt
    assert "row_id" in action.prompt and f'partition = "{partition}"' in action.prompt
    if template in {"clustering", "representation"}:
        assert "outcome" not in action.prompt
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    frame = pd.DataFrame({"row_id": [11, 21], "partition": [partition] * 2, "prediction": [0, 1]})
    saved = mlca_runtime.save_row_outputs(frame, output.name)
    pd.testing.assert_frame_equal(pd.read_parquet(saved), frame)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["outputs"][-1]["kind"] == "data"
    with pytest.raises(ValueError, match="Parquet"):
        mlca_runtime.save_row_outputs(frame, "old_predictions.csv")


def test_worker_api_explains_row_schema_without_relaxing_it(tmp_path, monkeypatch):
    api = runtime_api()
    for term in ["summary tables", ".parquet", "row_id", "partition", "validation is spelled val"]:
        assert term in api
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    with pytest.raises(ValueError, match="row_id and partition"):
        mlca_runtime.save_row_outputs(pd.DataFrame({"prediction": [1]}), "rows.parquet")
    with pytest.raises(ValueError, match="invalid partitions"):
        mlca_runtime.save_row_outputs(
            pd.DataFrame({"row_id": [0], "partition": ["validation"]}), "rows.parquet"
        )


@pytest.mark.parametrize("kind", ["binary", "multiclass"])
@pytest.mark.parametrize("split", ["val", "test"])
def test_classification_primary_metric_contract_stays_task_specific(tmp_path, monkeypatch, kind, split):
    action = get("tabular_classification").actions["score_validation" if split == "val" else "score_test"]
    assert "primary_metric" in action.prompt
    assert "Binary:" in action.prompt and "Multiclass:" in action.prompt
    assert "no binary threshold" in action.prompt
    assert "task-specific" in action.methods_text
    metric = default_metric(kind)
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    mlca_runtime.record_metric(metric, 0.75, split)
    metrics = json.loads((tmp_path / "manifest.json").read_text())["metrics"]
    state = NS(
        template_id="tabular_classification",
        task={"type": kind, "primary_metric": metric},
        steps=[{"status": "completed", "metrics": metrics}],
    )
    spec = {"type": "metric_present", "name": "primary", "split": split}
    assert evaluate(spec, state, tmp_path)[0]
    if kind == "multiclass":
        state.steps[0]["metrics"] = [{"name": "roc_auc", "split": split, "value": 0.75}]
        assert not evaluate(spec, state, tmp_path)[0]


@pytest.mark.parametrize(
    "error,hint",
    [
        (
            "roc_auc_score(PRIVATE_VALUE)\nTypeError: got an unexpected keyword argument 'pos_label'",
            "roc_auc_score has no pos_label",
        ),
        (
            "ValueError: multiclass-multioutput is not supported PRIVATE_VALUE",
            "Score categorical outputs separately",
        ),
        (
            "ValueError: Classification metrics can't handle a mix of PRIVATE_VALUE and multiclass targets",
            "Reuse training-fitted target encoders unchanged",
        ),
    ],
)
def test_scoring_diagnostics_are_fixed_and_value_free(error, hint):
    message = diagnostics({"stderr": error}, False)
    assert hint in message
    assert "PRIVATE_VALUE" not in message
