import json
from types import SimpleNamespace as NS

import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

import mlca_runtime
from mlca.engine.guided import _model_scene, validate_effect
from mlca.engine.options import fallback
from mlca.errors import MlcaUserError
from mlca.log.schema import ProjectState
from mlca.runner.run_step import diagnostics
from mlca.templates.registry import get


def test_navigator_sees_exact_effect_shapes_parameter_schema_and_local_goals(monkeypatch):
    workflow = get("clustering")
    state = ProjectState(current_event="eda", primary_data="source", data={"source": {}})
    calls = []

    def complete(role, messages, **kwargs):
        calls.append(messages[0]["content"])
        return NS(
            request_id="scripted",
            text=json.dumps(
                {
                    "situation": "Prepare the analysis units.",
                    "choices": [
                        {
                            "id": "1",
                            "action_id": "build_entities",
                            "params": {},
                            "title": "Prepare entities",
                            "why_now": "Build the declared analysis unit.",
                            "what_happens": "Prepare one row per unit.",
                            "recommended": True,
                        }
                    ],
                    "question": {
                        "header": "Preparation",
                        "question": "Prepare the declared analysis unit?",
                        "options": [
                            {
                                "label": "Prepare entities",
                                "description": "Run the declared preparation action",
                                "effect": {
                                    "kind": "choose_action",
                                    "action_id": "build_entities",
                                    "params": {},
                                },
                            }
                        ],
                        "recommended": 0,
                    },
                }
            ),
        )

    session = NS(state=state, workflow=workflow, client=NS(complete=complete))
    monkeypatch.setattr(
        "mlca.engine.guided.Navigator", lambda _: NS(context=lambda *_: None, rails_text=lambda: "")
    )
    scene, options, _ = _model_scene(session, fallback(state, workflow))
    assert options[0]["action_id"] == "build_entities" and scene.question
    message = calls[0]
    for term in [
        "current_subgoal_ids",
        "action_parameters",
        "action_contracts",
        "question_effect_examples",
        '"kind": "choose_action"',
        '"kind": "pause"',
        "empty parameter schema permits no invented parameters",
    ]:
        assert term in message
    assert '"build_entities": {}' in message
    for effect in [
        {"action_id": "build_entities", "params": {}},
        {"kind": "choose_action", "action_id": "build_entities", "params": {"undeclared_rule": "net"}},
    ]:
        with pytest.raises(MlcaUserError):
            validate_effect(session, effect)


def test_reconstruction_branches_score_frontend_space_and_only_declared_metrics(tmp_path, monkeypatch):
    X = pd.DataFrame(np.random.default_rng(2).normal(size=(16, 3)), columns=["a", "b", "c"])

    def frontend():
        return ColumnTransformer([("numeric", StandardScaler(), list(X.columns))]).set_output(
            transform="pandas"
        )

    pca = Pipeline([("frontend", frontend()), ("estimator", PCA(n_components=2))]).fit(X)
    target = frontend().fit_transform(X)
    mlp = Pipeline(
        [
            ("frontend", frontend()),
            (
                "estimator",
                MLPRegressor(hidden_layer_sizes=(2,), solver="lbfgs", max_iter=2000, random_state=0),
            ),
        ]
    ).fit(X, target)
    assert not hasattr(pca, "predict") and not hasattr(pca, "inverse_transform")
    assert not hasattr(mlp, "inverse_transform")
    metrics = []
    for name, model in [("pca", pca), ("autoencoder", mlp)]:
        baseline = model[:-1].transform(X)
        reconstructed = (
            model.steps[-1][1].inverse_transform(model.transform(X)) if name == "pca" else model.predict(X)
        )
        error = float(np.mean((np.asarray(baseline) - reconstructed) ** 2))
        assert np.isfinite(error)
        metrics.append({"model": name, "metric": "reconstruction_error", "value": error})
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    mlca_runtime.save_table(pd.DataFrame(metrics), "validation_metrics.csv")
    mlca_runtime.record_metric("reconstruction_error", min(x["value"] for x in metrics), "val")
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert all(o["kind"] == "table" for o in manifest["outputs"])
    assert not list(tmp_path.rglob("*embedding*"))
    action = get("representation").actions["score_validation"]
    assert "Validation requires only the declared metric summary" in action.prompt
    assert "MLPRegressor uses predict, not inverse_transform" in action.prompt
    assert all(o.kind == "table" for o in action.outputs)


@pytest.mark.parametrize(
    "error,expected",
    [
        (
            "AttributeError: This 'Pipeline' has no attribute 'inverse_transform' PRIVATE_VALUE",
            "Inspect each Pipeline",
        ),
        (
            "ValueError: MLCA: row outputs require row_id and partition",
            "Do not create undeclared row artifacts",
        ),
    ],
)
def test_repair_hints_are_fixed_and_do_not_send_captured_values(error, expected):
    text = diagnostics({"stderr": error}, False)
    assert expected in text and "PRIVATE_VALUE" not in text
