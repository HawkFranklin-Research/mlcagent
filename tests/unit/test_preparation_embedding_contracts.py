from types import SimpleNamespace as NS

import numpy as np
import pandas as pd
import pytest
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network._base import ACTIVATIONS

from mlca.errors import MlcaUserError
from mlca.runner.artefacts import collect
from mlca.runner.run_step import diagnostics
from mlca.templates.registry import get


@pytest.mark.parametrize(
    "change", ["rename_group", "missing_time", "null_group", "empty", "duplicate_index", None]
)
def test_prepared_fields_are_checked_before_step_completion(tmp_path, change):
    step = tmp_path / "step"
    (step / "outputs").mkdir(parents=True)
    frame = pd.DataFrame({"unit_key": ["a", "b", "c"], "period": [1, 2, 3], "value": [2.0, 3.0, 4.0]})
    if change == "rename_group":
        frame = frame.rename(columns={"unit_key": "entity_id"})
    if change == "missing_time":
        frame = frame.drop(columns="period")
    if change == "null_group":
        frame.loc[0, "unit_key"] = None
    if change == "empty":
        frame = frame.iloc[:0]
    if change == "duplicate_index":
        frame.index = [1, 1, 2]
    frame.to_parquet(step / "outputs/entities.parquet")
    state = NS(group_column="unit_key", task={"time_columns": ["period"]}, split=None)
    action = get("clustering").actions["build_entities"]
    if change:
        with pytest.raises(MlcaUserError) as exc:
            collect(tmp_path, step, action, state)
        assert exc.value.category == "missing_output"
    else:
        assert collect(tmp_path, step, action, state)["outputs"][0]["local_only"]
    assert "exact declared name" in action.prompt


def test_private_activation_returns_none_but_public_forward_returns_bottleneck():
    toy = np.array([[-1.0, 2.0], [3.0, -4.0]])
    result = ACTIVATIONS["relu"](toy)
    assert result is None
    np.testing.assert_array_equal(toy, [[0.0, 2.0], [3.0, 0.0]])
    X = np.random.default_rng(0).normal(size=(20, 3))
    model = MLPRegressor(hidden_layer_sizes=(4, 2, 4), solver="lbfgs", max_iter=2000, random_state=0).fit(
        X, X
    )
    middle = len(model.hidden_layer_sizes) // 2
    embedding = X
    for i in range(middle + 1):
        embedding = np.maximum(embedding @ model.coefs_[i] + model.intercepts_[i], 0)
    assert embedding.shape == (len(X), 2) and np.isfinite(embedding).all()
    hint = diagnostics(
        {"stderr": "AttributeError: 'NoneType' object has no attribute 'shape' PRIVATE_VALUE"}, False
    )
    assert "mutate their array and return None" in hint and "PRIVATE_VALUE" not in hint
