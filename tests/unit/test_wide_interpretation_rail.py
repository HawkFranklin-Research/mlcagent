"""Prompt-contract regression for wide interpretation; no data or live model calls."""

from types import SimpleNamespace as NS

import pytest

from mlca.engine.state_view import build
from mlca.paths import resource
from mlca.rails import load
from mlca.roles.worker import Worker, render_order
from mlca.templates.registry import get


def session(template="tabular_classification", problem="binary"):
    state = NS(
        task={"type": problem},
        template_id=template,
        current_event="interpret",
        steps=[],
        external=None,
        brief={},
        columns={},
        primary_data="synthetic",
        excluded_columns=[],
        subgoals={},
        facts={},
        inventory=[],
        artefacts={},
        test_unlocked=False,
    )
    return NS(state=state, packages=lambda: [], rails=load(resource("rails")), workflow=get(template))


@pytest.mark.parametrize(
    "template,problem",
    [
        ("tabular_classification", "binary"),
        ("tabular_classification", "multiclass"),
        ("multilabel_classification", "multilabel"),
        ("regression", "regression"),
        ("regression", "multioutput_regression"),
        ("clustering", "clustering"),
        ("representation", "representation"),
    ],
)
def test_wide_interpretation_budget_reaches_worker_work_order(template, problem):
    s = session(template, problem)
    assert s.rails.version == "rails-0.15"
    order = render_order(s, s.workflow.actions["explain_model"], {}, {}, s.state)
    for text in [order["instructions"], order["worker_prompt"]]:
        assert "[RL-0029]" in text
        assert "more than 500 input features" in text
        assert "top 50 features ranked by those importances with n_repeats <= 5" in text
        assert "complete frozen prediction input schema" in text
        assert "reliable importance ranking is unavailable" in text
        assert "within its time limit" in text
    assert "[RL-0029]" not in s.rails.instructions("navigator", "interpret", problem)
    assert "[RL-0029]" not in s.rails.instructions("worker", "model", problem)
    assert "[RL-0029]" not in s.rails.instructions("worker", "interpret", "survival")


def test_navigator_action_contract_bounds_the_existing_twenty_repeat_budget():
    s = session()
    action = build(s.state, s.workflow)["actions"]["explain_model"]
    text = action["prompt"]
    assert "For at most 500 input features" in text
    assert "20 repeats" in text  # Small inputs keep their existing repeat budget.
    assert "For more than 500 input features" in text
    assert "top 50 ranked by those importances with n_repeats <= 5" in text
    assert action["timeout_s"] == 300
    assert "recorded native model importances or validation permutation" in action["methods_text"]


def test_repair_keeps_the_bounded_interpretation_work_order(monkeypatch):
    s = session()
    action = s.workflow.actions["explain_model"]
    calls = []

    def complete(role, messages, **kwargs):
        calls.append(messages[0]["content"])
        return NS(text="```python\nimport mlca_runtime\npass\n```", request_id="offline-stub")

    s.client = NS(complete=complete)
    worker = Worker(s)
    monkeypatch.setattr(worker, "context", lambda *_: None)
    source, _ = worker.write_script(action, {}, {}, s.state, "synthetic-step")
    worker.repair_script(action, source, "Script timed out", "synthetic-step")
    assert len(calls) == 2
    for text in calls:
        assert "[RL-0029]" in text
        assert "top 50 features ranked by those importances with n_repeats <= 5" in text
