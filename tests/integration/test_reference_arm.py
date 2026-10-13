import pytest
import yaml

from mlca.api import Session
from mlca.errors import IntegrityError, MlcaUserError
from mlca.evaluation.bench import ApprovalPolicy, TaskCard, drive_guided
from mlca.evaluation.metrics import generate
from mlca.llm.usage import read
from mlca.project.init import initialise


def test_reference_is_explicit_and_cannot_be_switched(project_factory):
    root = project_factory()
    with Session(root) as s:
        assert s.measurement_arm == "worker"
        assert not (root / ".mlca/runtime/mlca_runtime/reference.py").exists()
    path = root / ".mlca/project.yaml"
    settings = yaml.safe_load(path.read_text())
    settings["config"]["measurement_arm"] = "reference"
    path.write_text(yaml.safe_dump(settings))
    with pytest.raises(IntegrityError, match="Measurement arm"):
        Session(root)


@pytest.mark.parametrize("task", ["binary", "multiclass", "survival"])
def test_reference_full_path_no_models(tmp_path, task):
    # Small representative classification, no provider configured.
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(37)
    x = rng.normal(size=(180, 4))
    frame = pd.DataFrame(x, columns=["a", "b", "c", "d"])
    frame["outcome"] = (x[:, 0] + rng.normal(size=180) > 0).astype(int)
    template = "tabular_classification"
    if task == "multiclass":
        frame["outcome"] = np.argmax(
            np.column_stack([x[:, 0], x[:, 1], -x[:, 0] - x[:, 1]]) + rng.normal(size=(180, 3)), axis=1
        )
    elif task == "survival":
        template = "survival"
        frame["time"] = rng.exponential(np.exp(-0.3 * x[:, 0])) + 0.1
        frame["event"] = rng.binomial(1, 0.75, size=180)
        frame = frame.drop(columns="outcome")
    data = tmp_path / "table.csv"
    frame.to_csv(data, index=False)
    brief = {
        "aim": "Predict a recorded outcome",
        "target": "outcome",
        "unit": "One sample",
        "repeated_subjects": "no",
    }
    if task == "survival":
        brief.update(target="time", duration="time", event_column="event")
    root = initialise(
        tmp_path / "reference",
        [data],
        template,
        brief,
        {"measurement_arm": "reference", "sandbox": {"allow_level_b": True}},
    )
    with Session(root, client="bench", principal="user:policy/012345abcdef", policy=True) as s:
        assert s.client.disabled
        assert (root / ".mlca/runtime/mlca_runtime/reference.py").is_file()
        with pytest.raises(MlcaUserError, match="driver"):
            Session(root, mode="brain")
        card = TaskCard(
            template=template,
            data=[str(data)],
            brief=brief,
            measurement_arm="reference",
            guided=True,
            approval_policy=ApprovalPolicy(confirm_subgoals=True, unlock_test=True),
        )
        drive_guided(s, card)
        assert s.state.current_event == "report"
        assert all(st["status"] == "completed" for st in s.state.steps)
        assert {st["action_id"] for st in s.state.steps} >= {
            "train_cox" if task == "survival" else "train_logistic",
            "train_alternative",
        }
        assert read(root) == []
        assert all(st["measurement_arm"] == "reference" for st in s.state.steps)
        metrics = generate(s)
        assert metrics["measurement_arm"] == "reference"
        assert metrics["results"]["test"]["value"]["value"] is not None
        s.store.verify()
