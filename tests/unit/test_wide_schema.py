"""Model-facing wide-table contexts; only synthetic data and stubbed providers."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pandas as pd
import pytest

from mlca.autonomous.inference import Inference, inventory, validate
from mlca.engine.state_view import build
from mlca.llm.egress import classify
from mlca.project.inventory import scan
from mlca.roles.base import prompt
from mlca.roles.worker import Worker, render_order
from mlca.schema_summary import model_view, summarize_frame, summarize_inventory


@pytest.fixture
def wide(tmp_path):
    rng = np.random.default_rng(9)
    frame = pd.DataFrame(rng.normal(size=(32, 25000)), columns=[f"feature_{i:05}" for i in range(25000)])
    frame["binary_label"] = np.arange(32) % 2
    frame["group_label"] = np.arange(32) % 5
    frame.loc[0, "feature_01000"] = np.nan
    path = tmp_path / "wide.parquet"
    frame.to_parquet(path)
    return frame, path


def test_setup_summary_keeps_required_columns_and_full_local_validation(wide):
    frame, path = wide
    schemas, tables = inventory([path], brief="Consider feature_12345")
    view = schemas[0]
    names = {c["name"] for c in view["columns"]}
    assert {
        "binary_label",
        "group_label",
        "feature_12345",
        *frame.columns[:20],
        *frame.columns[-20:],
    } <= names
    assert view["total_columns"] == 25002
    assert view["columns_omitted"] + len(names) == 25002
    block = view["numeric_blocks"][0]
    assert block["missing_values"] == block["columns_with_missing"] == 1
    assert block["min_range"][0] <= block["min_range"][1]
    assert len(block["example_names"]) == 20
    assert len(json.dumps(view).encode()) < 200000
    assert tables["wide"].equals(frame)
    proposal = Inference(
        primary_data="wide",
        problem_type="regression",
        targets=["feature_11111"],
        unit="sample",
        repeated_subjects="No",
        reason="Numeric outcome",
    )
    assert "feature_11111" not in names
    assert validate(proposal, tables) is proposal


def test_all_event_work_orders_navigator_and_repairs_are_bounded(wide, opened_project, monkeypatch):
    _, path = wide
    item = scan("wide", path)
    original = copy.deepcopy(item)
    summary = summarize_inventory(item)
    assert summary["numeric_blocks"][0]["missing_values"] == 1
    assert {c["name"] for c in summary["columns"]} >= {"binary_label", "group_label"}
    s = opened_project
    state = copy.deepcopy(s.state)
    state.inventory = [item]
    state.primary_data = "wide"
    state.data = {"wide": {}}
    state.brief = {"aim": "Predict binary_label"}
    state.columns = {"target": "binary_label"}
    state.excluded_columns = list(item["columns"])[100:1000]
    sent = []

    def complete(role, messages, **kwargs):
        payload = {"model": "offline", "messages": messages}
        sent.append(payload)
        assert classify(payload, [], False)["bytes_sent"] < 200000
        return NS(text="```python\nimport mlca_runtime\npass\n```", request_id="stub")

    worker = Worker(NS(client=NS(complete=complete)))
    monkeypatch.setattr(worker, "context", lambda *_: None)
    for event in s.workflow.events:
        state.current_event = event
        view = build(state, s.workflow)
        complete(
            "navigator", [{"role": "user", "content": prompt("navigator_options.md", state=view, schema={})}]
        )
        for action in (a for a in s.workflow.actions.values() if a.event == event):
            order = render_order(s, action, {}, {"_protocol": Path("protocol.json")}, state)
            complete("worker", [{"role": "user", "content": order["worker_prompt"]}])
            worker._original_order = order["worker_prompt"]
            worker.repair_script(action, "import mlca_runtime\npass", "ValueError", "stub")
    assert len(sent) > 30
    assert item == original  # Model compaction must never modify the local inventory.
    assert len(state.excluded_columns) == 900
    assert model_view(state.excluded_columns)["omitted_entries"] == 860


def test_small_schema_and_nonfinite_ranges():
    frame = pd.DataFrame({"a": [1, 2], "b": [0, 1]})
    view = summarize_frame(frame, name="small")
    assert len(view["columns"]) == 2 and view["columns_omitted"] == 0
    assert view["columns"][0]["value_counts"]
    item = {"columns": ["a"], "dtypes": {"a": "int64"}, "missing": {"a": 0}}
    assert summarize_inventory(item) == item
    from mlca.schema_summary import finite_bounds

    assert finite_bounds([np.nan, np.inf, None]) == [None, None]
    assert finite_bounds([np.nan, 1.0, 4.0]) == [1.0, 4.0]


def test_real_setup_request_and_egress_match_bounded_payload(wide, tmp_path, monkeypatch):
    from mlca.autonomous.inference import infer
    from mlca.llm.client import Client
    from mlca.paths import canonical

    _, path = wide
    proposal = Inference(
        primary_data="wide",
        problem_type="binary",
        targets=["binary_label"],
        unit="sample",
        repeated_subjects="No",
        reason="Predict observed categories",
    )
    sent = []

    def complete(payload):
        sent.append(copy.deepcopy(payload))
        return {
            "text": proposal.model_dump_json(),
            "input_tokens": 10,
            "output_tokens": 10,
            "cached_tokens": 0,
            "cost_usd": 0,
        }

    monkeypatch.setattr(Client, "_provider", lambda *_: NS(complete=complete))
    config = {
        "providers": {"offline": {"kind": "fake", "request_cost_bound_usd": 0}},
        "roles": {r: {"provider": "offline", "model": "stub"} for r in ("navigator", "worker")},
    }
    evidence = tmp_path / "setup"
    actual, _, _, _ = infer([path], "Predict binary_label", config, evidence)
    assert actual.targets == ["binary_label"]
    entries = [json.loads(line) for line in (evidence / ".mlca/egress.jsonl").read_text().splitlines()]
    assert len(entries) == len(sent) == 1
    assert entries[0]["bytes_sent"] == len(canonical(sent[0]).encode()) < 200000
    assert entries[0]["setup_inventory"][0]["total_columns"] == 25002
    assert len(entries[0]["setup_inventory"][0]["columns"]) < 100
