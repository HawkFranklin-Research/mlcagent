"""Pre-freeze support for the biomedical studies: sealed external cohorts and saved test predictions."""

import pandas as pd
import pytest

import mlca.autonomous.runner as runner
from mlca.errors import MlcaUserError


class Stop(Exception):
    pass


def tables(tmp_path):
    study = tmp_path / "study"
    study.mkdir()
    pd.DataFrame({"x": [1, 2, 3], "y": [0, 1, 0]}).to_csv(study / "discovery.csv", index=False)
    cohort = tmp_path / "cohort" / "external.csv"
    cohort.parent.mkdir()
    pd.DataFrame({"x": [4, 5], "y": [1, 0]}).to_csv(cohort, index=False)
    return study, cohort


def test_external_cohort_is_hidden_from_setup_and_registered_sealed(tmp_path, monkeypatch):
    study, cohort = tables(tmp_path)
    seen = {}

    def infer(paths, *args, **kwargs):
        seen["inferred"] = [p.name for p in paths]
        raise Stop()

    monkeypatch.setattr(runner, "infer", infer)
    runner.run(study, tmp_path / "out", external=[cohort])
    assert seen["inferred"] == ["discovery.csv"]

    def initialise(project, files, *args, data_roles=None, **kwargs):
        seen["files"] = [p.name for p in files]
        seen["roles"] = data_roles
        raise Stop()

    proposal = runner.Inference.model_validate(
        {
            "primary_data": "discovery",
            "problem_type": "binary",
            "targets": ["y"],
            "unit": "One observation",
            "repeated_subjects": "No",
            "reason": "Predict y",
        }
    )
    monkeypatch.setattr(runner, "infer", lambda *a, **k: (proposal, "request", "digest", "session"))
    monkeypatch.setattr(runner, "initialise", initialise)
    runner.run(study, tmp_path / "out2", external=[cohort])
    assert seen["files"] == ["discovery.csv", "external.csv"]
    assert seen["roles"] == {"external": "external"}


def test_external_cohort_inside_the_study_folder_is_refused(tmp_path):
    study, _ = tables(tmp_path)
    with pytest.raises(MlcaUserError, match="outside the study folder"):
        runner.run(study, tmp_path / "out", external=[study / "discovery.csv"])


def test_navigator_view_omits_external_cohort_schema():
    from types import SimpleNamespace as NS

    from mlca.engine.state_view import build

    workflow = NS(events={"data": NS(model_dump=dict, actions=[], id="data")}, actions={})
    state = NS(
        current_event="data",
        steps=[],
        subgoals={},
        facts={},
        brief={},
        columns={},
        artefacts={},
        test_unlocked=False,
        inventory=[{"name": "discovery", "columns": ["x"]}, {"name": "cohort", "columns": ["x"]}],
        data={"discovery": {"role": "discovery"}, "cohort": {"role": "external"}},
    )
    assert [i["name"] for i in build(state, workflow)["inventory"]] == ["discovery"]
