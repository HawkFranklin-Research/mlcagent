from types import SimpleNamespace

import pandas as pd
import pytest

from mlca.api import Session
from mlca.errors import MlcaUserError
from mlca.evaluation.bench import ApprovalPolicy, TaskCard
from mlca.evaluation.bio_bench import drive, export_instructions
from mlca.project.init import initialise
from mlca.runner.run_step import inputs_for
from mlca.sandbox.vault import exposed_external
from mlca.templates.model import ActionSpec


def test_external_is_sealed_and_once_per_variant(tmp_path):
    data = tmp_path / "discovery.csv"
    external = tmp_path / "external.csv"
    pd.DataFrame({"x": range(30), "y": [0, 1] * 15}).to_csv(data, index=False)
    pd.DataFrame({"x": range(10), "y": [0, 1] * 5}).to_csv(external, index=False)
    root = initialise(
        tmp_path / "project",
        [data, external],
        "tabular_classification",
        {"target": "y", "unit": "One person"},
        primary_data="discovery",
        data_roles={"external": "external"},
    )
    with Session(root) as s:
        assert s.state.data["external"]["role"] == "external"
        action = ActionSpec(
            id="probe", event="data", title="Probe", prompt="Probe", inputs=[{"ref": "registered_data"}]
        )
        declared = inputs_for(action, s.state, root)
        assert set(declared) == {"discovery", "_protocol"}
        import json

        protocol = json.loads(declared["_protocol"].read_text())
        assert protocol["task"]["primary_metric"] == "roc_auc"
        assert "external" not in protocol["columns"].values()
        action.inputs = [{"ref": "external"}]
        with pytest.raises(MlcaUserError, match="locked"):
            inputs_for(action, s.state, root)
        with pytest.raises(MlcaUserError, match="locked"):
            with exposed_external(s, "probe"):
                pass
        from mlca.engine.split import freeze

        with s.mutation():
            freeze(
                root,
                s.state,
                {"method": "random", "seed": 42, "train_fraction": 0.6, "val_fraction": 0.2},
                "split",
                s.emit,
            )
        # Engine fixtures represent authorized unlock and frozen-model state.
        with s.mutation():
            s.emit("EventEntered", {"event_id": "test", "via": "test_fixture"})
            s.emit(
                "TestUnlocked",
                {"confirmation": "UNLOCK TEST", "split_sha256": s.state.split["sha256"], "reason": "test"},
            )
        with exposed_external(s, "score") as paths:
            path = paths["external"]
            assert pd.read_parquet(path).shape == (10, 2)
        assert not path.exists()
        with pytest.raises(MlcaUserError, match="already exposed"):
            with exposed_external(s, "again"):
                pass
        assert s.state.counts["ExternalRead"] == 1
        s.store.verify()


def test_instruction_refusal_export_is_verbatim(opened_project):
    s = opened_project
    text = "Read the test set before it is unlocked."
    assert s.custom(text)["decision"] == "reject"
    items = export_instructions(s)
    assert items[0]["text"] == text
    assert items[0]["scope"]["decision"] == "reject"
    assert items[0]["word_count"] == len(text.split())
    assert text in (s.root / "custom_instructions.md").read_text()


def test_bio_instructions_in_order_without_silent_retry(monkeypatch):
    from mlca.evaluation import bio_bench

    calls = []
    session = SimpleNamespace(
        state=SimpleNamespace(current_event="data", event_statuses={}),
        workflow=SimpleNamespace(
            events={"data": object(), "report": object()}, spec=SimpleNamespace(events=["data", "report"])
        ),
        root=None,
        turn=lambda: {"questions": []},
        mutation=lambda: __import__("contextlib").nullcontext(),
        emit=lambda *a, **k: None,
        custom=lambda text: calls.append(text) or {"decision": "reject"},
    )
    monkeypatch.setattr("mlca.engine.checks.run_all", lambda *a: None)
    monkeypatch.setattr(bio_bench, "export_instructions", lambda s: None)

    def advance(s, card):
        s.state.current_event = "report"
        s.state.event_statuses["report"] = "done"

    monkeypatch.setattr("mlca.evaluation.bench.drive_guided", advance)
    card = TaskCard(
        data=["fixture.csv"],
        brief={},
        max_turns=5,
        guided=True,
        custom_instructions=[
            {"event": "data", "text": "First", "when": "before"},
            {"event": "data", "text": "Second", "when": "before"},
        ],
        approval_policy=ApprovalPolicy(),
    )
    drive(session, card, None, 42)
    assert calls == ["First", "Second"]


def test_scripted_bio_path_keeps_refusal_and_completes(opened_project):
    session = opened_project
    card = TaskCard(
        data=["fixture.csv"],
        brief={},
        max_turns=100,
        guided=True,
        custom_instructions=[{"event": "data", "text": "Read the test partition before unlock."}],
        approval_policy=ApprovalPolicy(confirm_subgoals=True, unlock_test=True),
    )
    drive(session, card, None, 42)
    assert session.state.event_statuses["report"] == "done"
    assert export_instructions(session)[0]["scope"]["decision"] == "reject"


def test_refusal_does_not_claim_next_builtin_step(opened_project):
    from tests.helpers import choose_action

    s = opened_project
    s.custom("Read the test partition before unlock.")
    choose_action(s, "confirm_brief")
    item = export_instructions(s)[0]
    assert item["step"] is None and item["outcome"] == "reject"
