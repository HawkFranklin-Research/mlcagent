"""Synthetic regression for duration mistakenly excluded as an input feature."""

from pathlib import Path

import pandas as pd
import pytest

from mlca.api import Session
from mlca.engine.data_review import findings, prepared
from mlca.engine.questions import review_training
from mlca.engine.split import freeze
from mlca.errors import MlcaUserError
from mlca.project.inventory import read_table


def test_survival_outcomes_survive_exclusions_and_training_review(project_factory, monkeypatch):
    with Session.open(project_factory(template="survival")) as s:
        with s.mutation():
            s.emit(
                "TaskConfigured",
                {
                    "task": {"type": "survival", "targets": ["observed"], "autonomous": True},
                    "excluded_columns": ["duration", "observed", "x4"],
                    "group_column": None,
                },
            )
            from mlca.engine.data_review import context_key

            s.emit("DataReviewStarted", {"context_sha256": context_key(s.state), "rules_version": "1"})
            path = prepared(s)
        table = read_table(path)
        assert {"duration", "observed"} <= set(table)
        assert "x4" not in table
        assert "duration" not in s.state.excluded_columns
        assert "observed" not in s.state.excluded_columns
        with s.mutation():
            freeze(
                s.root,
                s.state,
                {"method": "random", "seed": 42, "train_fraction": 0.6, "val_fraction": 0.2},
                "synthetic",
                s.emit,
            )
        train_path = s.root / s.state.split["train"]["path"]
        reads = []

        def only_train(path):
            reads.append(Path(path))
            assert Path(path) == train_path
            return pd.read_parquet(path)

        monkeypatch.setattr("mlca.project.inventory.read_table", only_train)
        with s.mutation():
            review_training(s)
        assert reads == [train_path]
        # Existing runtime guards continue to identify both fields as protected.
        import json

        from mlca.engine.data_review import protocol_input

        protocol = json.loads(protocol_input(s).read_text())
        assert protocol["columns"]["duration"] == "duration"
        assert protocol["columns"]["event_column"] == "observed"


def test_survival_duration_alias_and_missing_event_are_explicit():
    frame = pd.DataFrame({"followup": range(1, 41), "observed": [0, 1] * 20, "x": range(40)})
    findings(frame, {"duration": "followup", "event_column": "observed"}, "survival", phase="train")
    with pytest.raises(MlcaUserError, match="survival event column"):
        findings(frame, {"duration": "followup", "event_column": "missing"}, "survival")


def test_autonomous_setup_does_not_exclude_duration_suspect(tmp_path, opened_project, monkeypatch):
    import mlca.autonomous.runner as runner
    from mlca.autonomous.inference import Inference

    data = tmp_path / "survival.csv"
    pd.DataFrame({"followup": range(1, 41), "observed": [0, 1] * 20, "feature": range(40)}).to_csv(
        data, index=False
    )
    proposal = Inference(
        primary_data="survival",
        problem_type="survival",
        targets=["observed"],
        duration="followup",
        event_column="observed",
        leakage_suspects=["followup"],
        unit="sample",
        repeated_subjects="No",
        reason="Time to event",
    )
    monkeypatch.setattr(runner, "infer", lambda *a, **k: (proposal, "stub", "digest", "offline"))
    seen = []

    def stop(session):
        seen.append(session.state.excluded_columns)
        raise MlcaUserError("Synthetic setup-only stop")

    monkeypatch.setattr(runner, "drive", stop)
    runner.run(data, tmp_path / "out", config=opened_project.config.model_dump(mode="json"), halt_window=0)
    assert seen == [[]]
