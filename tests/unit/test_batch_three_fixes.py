from types import SimpleNamespace as NS

import pytest

from mlca.engine.options import Option, fallback, missing_validation_metric, validate
from mlca.templates.registry import get


@pytest.mark.parametrize(
    "template",
    [
        "tabular_classification",
        "multilabel_classification",
        "regression",
        "clustering",
        "representation",
        "survival",
    ],
)
@pytest.mark.parametrize("name", ["score_validation", "score_test"])
def test_every_scoring_action_uses_declared_nested_primary_metric(template, name):
    action = get(template).actions[name]
    assert "_protocol['task']['primary_metric']" in action.prompt
    assert "Record: metric " not in action.prompt
    assert "task-specific" in action.methods_text


def state(steps):
    return NS(
        current_event="validate",
        template_id="regression",
        task={"type": "regression", "primary_metric": "poisson_deviance"},
        event_statuses={"validate": "open"},
        generations={},
        subgoals={},
        primary_data="toy",
        data={"toy": {}},
        steps=steps,
    )


def test_missing_primary_metric_retries_scoring_once_without_reopening_fit():
    workflow = get("regression")
    step = {
        "status": "completed",
        "event_id": "validate",
        "action_id": "score_validation",
        "params": {},
        "metrics": [{"name": "rmse", "split": "val", "value": 1.0}],
    }
    current = state([step])
    assert missing_validation_metric(current)
    option = next(o for o in fallback(current, workflow) if o["action_id"] == "score_validation")
    assert "Retry validation" in option["why_now"]
    assert validate([Option.model_validate(option)], current, workflow)
    current.steps.append(dict(step))
    assert all(o["action_id"] != "score_validation" for o in fallback(current, workflow))
    with pytest.raises(Exception, match="Duplicate completed"):
        validate([Option.model_validate(option)], current, workflow)
    current.steps[-1]["metrics"] = [{"name": "poisson_deviance", "split": "val", "value": 0.2}]
    assert not missing_validation_metric(current)
