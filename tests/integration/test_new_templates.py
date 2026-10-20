import json

import numpy as np
import pandas as pd
import pytest
import yaml

from mlca.api import Session
from mlca.project.init import initialise
from mlca.templates.registry import get
from tests.helpers import choose_action


@pytest.mark.parametrize(
    "template,metric",
    [
        ("regression", "rmse"),
        ("multilabel_classification", "macro_f1"),
        ("clustering", "silhouette"),
        ("representation", "reconstruction_error"),
    ],
)
def test_new_template_scripted_to_report(tmp_path, template, metric):
    data = tmp_path / "synthetic.csv"
    x = np.random.default_rng(42).normal(size=(60, 3))
    frame = pd.DataFrame(x, columns=["feature_a", "feature_b", "feature_c"])
    targets = []
    if template in {"regression", "multilabel_classification"}:
        targets = ["outcome_a", "outcome_b"]
        frame["outcome_a"] = x[:, 0] if template == "regression" else (x[:, 0] > 0).astype(int)
        frame["outcome_b"] = x[:, 1] if template == "regression" else (x[:, 1] > 0).astype(int)
    frame.to_csv(data, index=False)
    workflow = get(template)
    responses = []
    for action in workflow.actions.values():
        if action.builtin or action.role == "supporting":
            continue
        if action.event in {"preprocess", "features", "model"}:
            # This is deliberately minimal fixture code, not a scientific acceptance run.
            source = """import mlca_runtime as rt
import pandas as pd
from sklearn.preprocessing import StandardScaler
train=pd.read_parquet(rt.inputs()['train'])
model=rt.fit_record(StandardScaler(), train[['feature_a','feature_b','feature_c']], 'train')
"""
            source += f"rt.save_model(model, {action.outputs[0].name!r})\n"
        else:
            source = "import mlca_runtime as rt\nimport pandas as pd\n"
            for output in action.outputs:
                if output.kind == "data":
                    parts = output.row_partitions or ["train", "test"]
                    for part in parts:
                        source += f'{part}=pd.read_parquet(rt.inputs()["{part}"])\n'
                    ids = "+".join(f"list({part}.index)" for part in parts)
                    labels = "+".join(f'["{part}"]*len({part})' for part in parts)
                    source += f'rows=pd.DataFrame({{"row_id":{ids},"partition":{labels}}})\n'
                    source += (
                        'rows["cluster"]=0\n' if template == "clustering" else 'rows["embedding_0"]=0.0\n'
                    )
                    source += f"rt.save_row_outputs(rows, {output.name!r})\n"
                elif output.kind == "table":
                    source += f'rt.save_table(pd.DataFrame({{"metric":["fixture"],"value":[0.5]}}), {output.name!r})\n'
                else:
                    source += f'rt.save_json({{"fixture":True}}, {output.name!r})\n'
            if action.event in {"validate", "test"}:
                source += f"rt.record_metric({metric!r}, 0.5, {'val' if action.event == 'validate' else 'test'!r})\n"
        responses.append(
            {"match": {"role": "worker", "action_id": action.id}, "text": "```python\n" + source + "```"}
        )
    script = tmp_path / "script.yaml"
    script.write_text(yaml.safe_dump({"responses": responses}))
    config = {
        "providers": {"fake": {"kind": "fake", "script": str(script)}},
        "roles": {"worker": {"provider": "fake", "model": "scripted"}},
        "sandbox": {"allow_level_b": True},
    }
    root = initialise(
        tmp_path / "project",
        [data],
        template,
        {
            "target": targets[0] if targets else "",
            "targets": json.dumps(targets),
            "unit": "One row is one observation",
        },
        config,
    )
    with Session.open(root) as session:
        while True:
            event = session.state.current_event
            if event == "test":
                session.unlock_test("UNLOCK TEST", "Fixture evaluation")
            choose_action(session, session.workflow.events[event].default_options[0])
            for goal in session.workflow.events[event].subgoals:
                if goal.check.type == "user_confirm":
                    session.confirm(goal.id, "Fixture approval")
            assert session.state.event_statuses[event] == "done", session.state.subgoals
            if event == "report":
                break
            session.next()
        assert session.store.verify()["ok"]


def test_registration_removes_labels_before_inventory_and_inputs(tmp_path, monkeypatch):
    from mlca.paths import sha256
    from mlca.runner.run_step import inputs_for

    data = tmp_path / "source.csv"
    pd.DataFrame({"visible": [1, 2, 3, 4], "secret_label": ["private-a", "private-b"] * 2}).to_csv(
        data, index=False
    )

    def environment(root, packages):
        (root / ".mlca/requirements.lock").write_text("")
        return {
            "packages": [],
            "lock_sha256": sha256(root / ".mlca/requirements.lock"),
            "runtime_sha256": "unused",
        }

    monkeypatch.setattr("mlca.project.init.create", environment)
    root = initialise(
        tmp_path / "project",
        [data],
        "clustering",
        {"unit": "One row is one observation"},
        exclude_columns=["secret_label"],
    )
    with Session.open(root) as session:
        assert session.state.inventory[0]["columns"] == ["visible"]
        paths = inputs_for(session.workflow.actions["audit_schema"], session.state, root)
        assert list(pd.read_parquet(next(iter(paths.values()))).columns) == ["visible"]
    # Labels and their names never enter any project text or Parquet schema.
    for file in (root / ".mlca").rglob("*"):
        if file.is_file() and file.suffix in {".json", ".jsonl", ".yaml"}:
            assert "secret_label" not in file.read_text()
            assert "private-a" not in file.read_text()
    assert pd.read_csv(data).columns.tolist() == ["visible", "secret_label"]


def test_excluded_external_table_can_be_sealed_atomically(tmp_path, monkeypatch):
    import io

    from mlca.paths import sha256
    from mlca.sandbox import vault

    sealed_columns = []
    seal = vault.seal

    def spy(project_id, key_id, data, destination):
        sealed_columns.append(list(pd.read_parquet(io.BytesIO(data)).columns))
        return seal(project_id, key_id, data, destination)

    monkeypatch.setattr(vault, "seal", spy)

    source, external = tmp_path / "source.csv", tmp_path / "external.csv"
    for path in [source, external]:
        pd.DataFrame({"visible": [1, 2, 3, 4], "hidden": ["a", "b", "a", "b"]}).to_csv(path, index=False)

    def environment(root, packages):
        (root / ".mlca/requirements.lock").write_text("")
        return {
            "packages": [],
            "lock_sha256": sha256(root / ".mlca/requirements.lock"),
            "runtime_sha256": "unused",
        }

    monkeypatch.setattr("mlca.project.init.create", environment)
    root = initialise(
        tmp_path / "project",
        [source, external],
        "clustering",
        {"unit": "One row"},
        primary_data="source",
        data_roles={"external": "external"},
        exclude_columns=["hidden"],
    )
    with Session.open(root) as session:
        assert any(r.type.value == "ExternalSealed" for r in session.store.read())
        assert sealed_columns == [["visible"]]
        assert "hidden" not in json.dumps(session.state.inventory)
