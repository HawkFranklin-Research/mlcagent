from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from mlca.roles.worker import render_order
from mlca.templates.registry import get


@pytest.mark.parametrize(
    "template,metric",
    [("tabular_classification", "roc_auc"), ("regression", "poisson_deviance"), ("survival", "c_index")],
)
def test_scoring_only_recovery_names_exact_selected_model_metric(template, metric):
    workflow = get(template)
    state = NS(
        task={"primary_metric": metric, "type": template},
        template_id=template,
        current_event="validate",
        generations={},
        steps=[
            {
                "status": "completed",
                "event_id": "validate",
                "action_id": "score_validation",
                "metrics": [{"name": metric + ":candidate", "split": "val", "value": 0.7}],
            }
        ],
        external=None,
        brief={},
        columns={},
        primary_data="toy",
        excluded_columns=[],
    )
    session = NS(state=state, packages=lambda: [], rails=None)
    order = render_order(
        session, workflow.actions["score_validation"], {}, {"_protocol": Path("protocol.json")}, state
    )
    assert f'record_metric("{metric}", value, split="val")' in order["worker_prompt"]
    assert "Per-model metric names are additional and do not count" in order["worker_prompt"]
    assert "without fitting" in order["worker_prompt"]
    state.steps[0]["metrics"][0]["name"] = metric
    assert (
        "Scoring-only recovery:"
        not in render_order(session, workflow.actions["score_validation"], {}, {}, state)["worker_prompt"]
    )
