"""Regression tests for the engine fixes after the first acceptance batch (B-0027 to B-0031)."""

from types import SimpleNamespace as NS

import pandas as pd
import pytest
from pydantic import ValidationError

import mlca_runtime as rt
from mlca.autonomous.inference import Inference
from mlca.engine.guided import Scene
from mlca.engine.options import Option
from mlca.engine.split import partitions
from mlca.errors import MlcaUserError
from mlca.runner.run_step import protected_columns

PROPOSAL = {
    "primary_data": "sheet",
    "problem_type": "binary",
    "targets": ["label"],
    "unit": "One observation",
    "repeated_subjects": "No",
    "reason": "Predict an outcome",
}


def time_params():
    return {"method": "time", "time_column": "day", "train_fraction": 0.6, "val_fraction": 0.2, "seed": 42}


def test_time_split_moves_boundaries_to_timestamp_changes():
    # Ten periods of 24 rows: the requested 60/20 cut points fall inside a period.
    frame = pd.DataFrame({"day": [d for d in range(10) for _ in range(24)], "hour": list(range(24)) * 10})
    frame = frame.sample(frac=1, random_state=1)
    labels = partitions(frame, {**time_params(), "train_fraction": 0.55, "val_fraction": 0.25}, "")
    assert labels.groupby(frame.day).nunique().max() == 1
    blocks = [frame.loc[labels.eq(x), "day"] for x in ["train", "val", "test"]]
    assert all(len(b) for b in blocks)
    assert blocks[0].max() < blocks[1].min() and blocks[1].max() < blocks[2].min()


def test_time_split_without_ties_keeps_exact_fractions():
    frame = pd.DataFrame({"day": range(101)})
    labels = partitions(frame, time_params(), "")
    assert labels.value_counts().to_dict() == {"train": 60, "val": 20, "test": 21}


def test_time_split_needs_three_distinct_timestamps():
    frame = pd.DataFrame({"day": [0] * 5 + [1] * 5})
    with pytest.raises(MlcaUserError, match="three distinct timestamps"):
        partitions(frame, time_params(), "")


def test_empty_nested_alternatives_are_dropped_but_content_stays_invalid():
    nested = {**PROPOSAL, "alternatives": [{**PROPOSAL, "alternatives": []}]}
    assert len(Inference.model_validate(nested).alternatives) == 1
    with pytest.raises(ValidationError):
        Inference.model_validate({**PROPOSAL, "alternatives": [{**PROPOSAL, "alternatives": [PROPOSAL]}]})


def test_long_display_text_is_clipped_not_rejected():
    words = " ".join(f"word{i}" for i in range(40))
    choice = {
        "id": "2",
        "action_id": "build_entities",
        "params": {},
        "title": words,
        "why_now": "x" * 300,
        "what_happens": words,
        "recommended": True,
    }
    scene = Scene.model_validate({"situation": "s" * 400, "choices": [choice]})
    picked = scene.choices[0]
    assert picked.action_id == "build_entities" and picked.recommended
    assert len(scene.situation) <= 240 and len(picked.why_now) <= 200
    assert len(picked.title.split()) <= 8 and len(picked.what_happens.split()) <= 20
    assert Option.model_validate({k: v for k, v in choice.items() if k not in {"what_happens", "recommended"}})


def test_fit_record_refuses_protected_columns(tmp_path, monkeypatch):
    class Estimator:
        def fit(self, X, y=None):
            return self

    frame = pd.DataFrame({"x1": [1.0, 2.0], "y1": [3.0, 4.0]}, index=[5, 9])
    monkeypatch.setenv("MLCA_STEP_DIR", str(tmp_path))
    monkeypatch.setenv("MLCA_TRAIN_INDEX_SHA256", rt.index_sha256(frame.index))
    monkeypatch.setenv("MLCA_PROTECTED_COLUMNS", '["unit", "y1"]')
    with pytest.raises(rt.FitRuleError, match=r"^MLCA: .*\['y1'\]"):
        rt.fit_record(Estimator(), frame, "train")
    rt.fit_record(Estimator(), frame[["x1"]], "train", y=frame["y1"])


def test_protected_columns_cover_outcomes_exclusions_and_group_except_survival_fields():
    state = NS(
        excluded_columns=["code"],
        task={"targets": ["y1", "y2"]},
        group_column="unit",
        columns={"target": "y1", "duration": None, "event_column": None},
        template_id="regression",
    )
    assert protected_columns(state) == ["code", "unit", "y1", "y2"]
    survival = NS(
        excluded_columns=[],
        task={"targets": []},
        group_column=None,
        columns={"target": None, "duration": "time", "event_column": "event"},
        template_id="survival",
    )
    assert protected_columns(survival) == []


def test_setup_failure_keeps_engine_message(tmp_path, monkeypatch):
    import mlca.autonomous.runner as runner

    data = tmp_path / "table.csv"
    pd.DataFrame({"x": [1, 2, 3], "y": [0, 1, 0]}).to_csv(data, index=False)

    def fail(*args, **kwargs):
        args[3].mkdir()
        raise MlcaUserError("Project environment command failed: no space left", category="invalid_request")

    monkeypatch.setattr(runner, "infer", fail)
    result = runner.run(data, tmp_path / "out")
    assert result["runs"][0]["message"] == (
        "Setup failed: MlcaUserError: Project environment command failed: no space left"
    )
