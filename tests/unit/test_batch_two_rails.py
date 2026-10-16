import numpy as np
import pytest
from sklearn.metrics import f1_score, roc_auc_score

from mlca.paths import resource
from mlca.rails import load
from mlca.templates.registry import get


def test_entity_preparation_reaches_the_navigator_before_split():
    rails = load(resource("rails"))
    text = rails.instructions("navigator", "eda", "clustering")
    assert "[RL-0020]" in text and "recommend build_entities before" in text
    assert "[RL-0020]" not in rails.instructions("navigator", "eda", "regression")
    assert "[RL-0020]" not in rails.instructions("navigator", "split", "clustering")
    action = get("clustering").actions["build_entities"]
    assert action.prepares_data == "entities.parquet"
    assert action.event == "eda" and action.outputs[0].kind == "data"


def test_feature_derivations_are_part_of_the_saved_contract():
    rails = load(resource("rails"))
    for event in ["preprocess", "features", "model", "validate", "test", "interpret"]:
        text = rails.instructions("worker", event, "regression")
        assert "[RL-0026]" in text and "transient DataFrame mutations" in text
        assert "Learned transforms fit only on the frozen training rows" in text
    assert "[RL-0026]" not in rails.instructions("navigator", "onboard", "regression")


def test_auc_contract_aligns_both_sides_without_an_unsupported_keyword():
    # Tiny metric-API regression, not an analysis or a reference-arm run.
    labels = np.array(["negative", "positive", "negative", "positive"])
    positive_probability = np.array([0.1, 0.9, 0.2, 0.8])
    with pytest.raises(TypeError, match="pos_label"):
        roc_auc_score(labels, positive_probability, pos_label="positive")
    assert roc_auc_score(labels == "positive", positive_probability) == 1.0
    text = load(resource("rails")).instructions("worker", "validate", "binary")
    assert "roc_auc_score does not accept pos_label" in text
    assert "binary indicator for that same label" in text


def test_categorical_output_metric_uses_matching_vectors_per_target():
    # Reproduce the observed library shape/dtype refusal using four toy rows.
    truth = np.array([[0, 0], [1, 1], [2, 0], [0, 1]])
    predicted = truth.astype(object)
    with pytest.raises(ValueError):
        f1_score(truth, predicted, average="macro")
    per_target = [
        f1_score(truth[:, i], predicted[:, i].astype(truth.dtype), average="macro")
        for i in range(truth.shape[1])
    ]
    assert np.mean(per_target) == 1.0
    text = load(resource("rails")).instructions("worker", "validate", "multilabel")
    assert "one-dimensional true and predicted labels" in text
    assert "Never fit an encoder during validation or test" in text


def test_temporal_rail_does_not_depend_on_a_forecasting_aim():
    text = load(resource("rails")).instructions("navigator", "onboard", "regression")
    assert "consecutive periods of one series, regardless of the stated prediction aim" in text


def test_pca_reconstructs_without_a_predict_method():
    from sklearn.decomposition import PCA
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    X = np.array([[0.0, 1.0, 2.0], [1.0, 2.0, 4.0], [2.0, 3.0, 5.0], [3.0, 5.0, 8.0]])
    frontend = StandardScaler().fit(X)
    pca = PCA(n_components=2).fit(frontend.transform(X))
    pipe = Pipeline([("scale", frontend), ("pca", pca)])
    assert not hasattr(pipe, "predict")
    reconstructed = pca.inverse_transform(pipe.transform(X))
    assert reconstructed.shape == X.shape
    assert np.isfinite(np.mean((reconstructed - frontend.transform(X)) ** 2))
    text = load(resource("rails")).instructions("worker", "validate", "representation")
    assert "PCA has no predict method" in text
    assert "inverse_transform(transform(X))" in text
