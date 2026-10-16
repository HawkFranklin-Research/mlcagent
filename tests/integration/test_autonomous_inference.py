import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from mlca.autonomous.inference import Inference, inventory, validate
from mlca.autonomous.runner import run
from mlca.errors import MlcaUserError
from mlca.llm.usage import read


def proposal(**changes):
    return Inference.model_validate(
        {
            "primary_data": "sheet",
            "problem_type": "binary",
            "targets": ["label"],
            "unit": "One row is one observation",
            "repeated_subjects": "No",
            "reason": "Predict the categorical outcome",
            **changes,
        }
    )


def test_schema_excludes_labels_and_never_reads_manifest(tmp_path, monkeypatch):
    data = tmp_path / "sheet.csv"
    pd.DataFrame({"feature": [1, 2, 3, 4], "label": [0, 1, 0, 1], "hidden": [7, 8, 7, 8]}).to_csv(
        data, index=False
    )
    (tmp_path / "manifest.yaml").write_text("POISON: do not load this")
    original = Path.read_text

    def read_text(path, *args, **kwargs):
        if path.name == "manifest.yaml":
            pytest.fail("Runtime read a researcher manifest")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read_text)
    schemas, tables = inventory([tmp_path], ["hidden"])
    assert "hidden" not in json.dumps(schemas)
    assert validate(proposal(), tables).template == "tabular_classification"
    for bad in [
        proposal(targets=["absent"]),
        proposal(problem_type="clustering"),
        proposal(problem_type="binary", targets=[]),
    ]:
        with pytest.raises(MlcaUserError):
            validate(bad, tables)


def test_bare_csv_scripted_run(tmp_path):
    import numpy as np

    rng = np.random.default_rng(0)
    x = rng.normal(size=(120, 4))
    frame = pd.DataFrame(x, columns=["x1", "x2", "x3", "x4"])
    frame["y"] = (x[:, 0] + rng.normal(size=120) > 0).astype(int)
    data = tmp_path / "sheet.csv"
    frame.to_csv(data, index=False)
    response = proposal(targets=["y"]).model_dump()
    responses = yaml.safe_load((Path(__file__).parents[1] / "fixtures/synthetic_fake_llm.yaml").read_text())
    baseline = next(
        r for r in responses["responses"] if r.get("match", {}).get("action_id") == "train_logistic"
    )
    responses["responses"].insert(
        0, {"match": {"role": "navigator", "purpose": "inference"}, "response": response}
    )
    responses["responses"].append(
        {
            "match": {"role": "worker", "action_id": "train_alternative"},
            "text": baseline["text"].replace("model.pkl", "alternative_model.pkl"),
        }
    )
    # Autonomous preparation preserves row IDs in Parquet. The scripted Worker
    # follows the declared format just as the live Worker is instructed to do.
    for item in responses["responses"]:
        if item.get("match", {}).get("role") == "worker" and "pd.read_csv(" in item.get("text", ""):
            item["text"] = item["text"].replace("pd.read_csv(", "read_declared(")
            import re

            item["text"] = re.sub(
                r"(import pandas as pd[^\n]*\n)",
                r"\1def read_declared(path, **kwargs):\n    return pd.read_parquet(path) if path.suffix == '.parquet' else pd.read_csv(path, **kwargs)\n",
                item["text"],
                count=1,
            )
    script = tmp_path / "responses.yaml"
    script.write_text(yaml.safe_dump(responses))
    config = {
        "providers": {"fake": {"kind": "fake", "script": str(script), "request_cost_bound_usd": 0}},
        "roles": {r: {"provider": "fake", "model": "scripted"} for r in ["navigator", "worker"]},
        "sandbox": {"allow_level_b": True},
    }
    out = tmp_path / "out"
    result = run(data, out, config=config, halt_window=0)
    assert result["runs"][0]["status"] == "completed", result
    project = out / "run-001"
    records = [json.loads(line) for line in (project / ".mlca/log/events.jsonl").read_text().splitlines()]
    assert any(r["type"] == "InferenceRecorded" for r in records)
    assert any(r["type"] == "QuestionAutoResolved" for r in records) or not any(
        r["type"] == "QuestionAsked" for r in records
    )
    inference_requests = [r for r in read(project) if r.get("purpose") == "inference"]
    assert inference_requests
    assert all(r["principal"] == result["policy_principal"] for r in inference_requests)
    metrics = json.loads((project / "reports/generated/metrics.json").read_text())
    assert metrics["run"]["completed"]["value"]
    assert metrics["autonomy"]["halts"]["value"] == 0
    assert len(metrics["autonomy"]["inference"]["choices"]) == 1
    assert metrics["models"]["navigator"]["calls"]["value"] == sum(
        r.get("role") == "navigator" for r in read(project)
    )
    from mlca.paths import resource
    from mlca.rails import load as load_rails

    assert metrics["autonomy"]["rails"]["version"] == load_rails(resource("rails")).version
    assert any(r["type"] == "DecisionWindowOpened" and r["payload"]["kind"] == "approval" for r in records)
    assert any(r["type"] == "DecisionWindowOpened" and r["payload"]["kind"] == "choice" for r in records)
    assert {r["actor"] for r in records if r["type"] == "UserConfirmed"} == {result["policy_principal"]}


@pytest.mark.parametrize(
    "kind,targets,metric",
    [
        ("binary", ["label"], "roc_auc"),
        ("multiclass", ["many"], "roc_auc_ovr"),
        ("multilabel", ["label", "many"], "macro_f1"),
        ("regression", ["numeric"], "rmse"),
        ("multioutput_regression", ["numeric", "numeric2"], "rmse"),
        ("clustering", [], "silhouette"),
        ("representation", [], "reconstruction_error"),
        ("survival", ["numeric"], "c_index"),
    ],
)
def test_explicit_default_metric_is_valid(kind, targets, metric):
    frame = pd.DataFrame(
        {
            "label": [0, 1, 0, 1],
            "many": [0, 1, 2, 0],
            "numeric": [1.0, 2.0, 3.0, 4.0],
            "numeric2": [2.0, 3.0, 4.0, 5.0],
        }
    )
    changes = {"problem_type": kind, "targets": targets, "primary_metric": metric}
    if kind == "survival":
        changes.update(duration="numeric", event_column="label")
    assert validate(proposal(**changes), {"sheet": frame}).primary_metric == metric


def test_nondefault_regression_metric_needs_reason():
    frame = pd.DataFrame({"numeric": [1.0, 2.0, 3.0, 4.0]})
    request = proposal(problem_type="regression", targets=["numeric"], primary_metric="mae")
    with pytest.raises(MlcaUserError):
        validate(request, {"sheet": frame})
    request.metric_reason = "Absolute error matches the study objective"
    assert validate(request, {"sheet": frame}).primary_metric == "mae"
