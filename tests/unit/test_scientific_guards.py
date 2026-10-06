import pandas as pd
import pytest

import mlca_runtime
from mlca.runner.static_checks import check


def test_readonly_fit_stage_refusal():
    message = "Steps in this event must fit on the training partition with fit_record. For read-only inspection, use the validate or interpret event."
    assert message in check('print("inspect")', require_fit=True)
    assert check("estimator.fit(X)", require_fit=True)
    assert check("import socket", require_fit=False)


def test_fit_exact_index_and_counts(monkeypatch):
    monkeypatch.setenv("MLCA_TRAIN_INDEX_SHA256", mlca_runtime.index_sha256([0, 1, 2]))
    monkeypatch.setenv("MLCA_TRAIN_ROW_COUNT", "3")
    with pytest.raises(ValueError, match="expected 3 rows, received 2 rows"):
        mlca_runtime.fit_record(object(), pd.DataFrame({"x": [1, 2]}), "train")
    with pytest.raises(ValueError, match="expected 3 rows, received 3 rows"):
        mlca_runtime.fit_record(object(), pd.DataFrame({"x": [1, 2, 3]}, index=[1, 2, 3]), "train")
    with pytest.raises(ValueError, match="only on training"):
        mlca_runtime.fit_record(object(), pd.DataFrame({"x": [1]}), "val")
