import pandas as pd
import pytest
import yaml

from mlca.engine.data_review import findings
from mlca.errors import MlcaUserError
from mlca.evaluation.bench import run


def test_numeric_separation_kept_and_mapping_excluded():
    f = pd.DataFrame(
        {
            "outcome": [0] * 20 + [1] * 20,
            "strong": list(range(40)),
            "coded": [0] * 20 + [1] * 20,
            "outcome_copy": list(range(40)),
        }
    )
    assert not any(
        q["key"] == "leakage:strong"
        for q in findings(f, {"target": "outcome"}, "tabular_classification", phase="pre")
    )
    qs = {q["key"]: q for q in findings(f, {"target": "outcome"}, "tabular_classification", phase="train")}
    assert qs["leakage:strong"]["options"][0]["effect"]["kind"] == "keep"
    assert qs["leakage:coded"]["options"][0]["effect"]["kind"] == "exclude_column"
    assert qs["leakage:outcome_copy"]["options"][0]["effect"]["kind"] == "exclude_column"


def test_training_review_never_reads_other_rows(opened_project, monkeypatch):
    from mlca.engine.questions import review_training
    from mlca.engine.split import freeze
    from mlca.paths import sha256
    from mlca.project.inventory import read_table

    s = opened_project
    with s.mutation():
        freeze(
            s.root,
            s.state,
            {"method": "random", "seed": 42, "train_fraction": 0.6, "val_fraction": 0.2},
            "split",
            s.emit,
        )
        s.emit("EventEntered", {"event_id": "preprocess", "via": "fixture"})
    path = s.root / s.state.split["train"]["path"]
    train = read_table(path)
    train["planted"] = train["y"]
    train.to_parquet(path)
    # Recorded fixture split describes the planted immutable train table.
    split = dict(s.state.split)
    split["train"] = {"path": str(path.relative_to(s.root)), "sha256": sha256(path)}
    with s.mutation():
        s.emit("SplitFrozen", split)
    calls = []

    def only_train(p):
        calls.append(p)
        assert p == path
        return train

    monkeypatch.setattr("mlca.project.inventory.read_table", only_train)
    with s.mutation():
        qs = review_training(s)
    assert calls == [path]
    q = next(q for q in qs if q["key"] == "train:leakage:planted")
    s.answer_question(q["question_id"], 0)
    assert "planted" in s.state.excluded_columns


def test_invalid_card_reports_field(tmp_path):
    card = tmp_path / "bad.yaml"
    card.write_text(yaml.safe_dump({"data": ["x.csv"], "brief": {}, "max_turns": 0}))
    with pytest.raises(MlcaUserError, match="max_turns"):
        run(card, 1, tmp_path / "out")
