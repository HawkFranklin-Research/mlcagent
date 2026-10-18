"""Rail selection for the rails-0.11 corrections (L-0010)."""

import numpy as np
from sklearn.metrics import roc_auc_score

from mlca.paths import resource
from mlca.rails import load


def test_datetime_rail_reaches_entity_and_model_steps():
    rails = load(resource("rails"))
    for event in ["eda", "preprocess", "features", "model"]:
        assert "[RL-0010]" in rails.instructions("worker", event, "clustering")
    assert "created in earlier steps" in rails.instructions("worker", "model", "clustering")
    assert "[RL-0010]" not in rails.instructions("navigator", "model", "clustering")


def test_raw_column_transformers_are_never_chained():
    rails = load(resource("rails"))
    for event in ["features", "model", "validate", "test", "interpret"]:
        assert "[RL-0027]" in rails.instructions("worker", event, "representation")
    assert "[RL-0027]" not in rails.instructions("worker", "preprocess", "representation")


def test_partition_missing_classes_uses_mean_binary_auc():
    text = load(resource("rails")).instructions("worker", "validate", "multiclass")
    assert "lacks some model classes" in text and "roc_auc_score(y_true == c" in text
    # The prescribed value equals the multiclass macro AUC when every class is present.
    rng = np.random.default_rng(0)
    proba = rng.dirichlet(np.ones(3), size=60)
    y = np.arange(60) % 3
    mean = np.mean([roc_auc_score(y == c, proba[:, c]) for c in range(3)])
    assert np.isclose(mean, roc_auc_score(y, proba, multi_class="ovr", average="macro"))
