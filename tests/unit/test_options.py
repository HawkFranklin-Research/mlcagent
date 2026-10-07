from mlca.engine.options import fallback
from mlca.log.schema import ProjectState
from mlca.templates.registry import get


def test_fallback_alternative_and_done():
    workflow = get("tabular_classification")
    state = ProjectState(
        current_event="model",
        generations={"model": 1},
        steps=[
            {
                "status": "completed",
                "action_id": "train_logistic",
                "params": {},
                "event_id": "model",
                "generation": 1,
            }
        ],
    )
    assert [o["action_id"] for o in fallback(state, workflow)] == ["train_alternative"]
    state.event_statuses["model"] = "done"
    assert fallback(state, workflow) == []


def test_exhausted_parameterless_and_parameterized():
    workflow = get("tabular_classification")
    state = ProjectState(
        current_event="model",
        steps=[
            {"status": "completed", "action_id": name, "params": {}, "event_id": "model"}
            for name in ("train_logistic", "train_alternative")
        ],
    )
    assert fallback(state, workflow) == []
    state = ProjectState(current_event="split")
    options = fallback(state, workflow)
    state.steps = [
        {"status": "completed", "action_id": o["action_id"], "params": o["params"], "event_id": "split"}
        for o in options
    ]
    repeats = fallback(state, workflow)
    assert repeats and all(o["why_now"] == "Repeat with different parameters" for o in repeats)


def test_supporting_actions_before_and_after_completion():
    workflow = get("tabular_classification")
    state = ProjectState(current_event="data", generations={"data": 1})
    assert [o["action_id"] for o in fallback(state, workflow)] == ["audit_schema", "count_target"]
    state.event_statuses["data"] = "done"
    assert [o["action_id"] for o in fallback(state, workflow)] == ["count_target"]
    state.steps = [
        {
            "status": "completed",
            "action_id": "count_target",
            "params": {},
            "event_id": "data",
            "generation": 1,
        }
    ]
    assert fallback(state, workflow) == []
    state.generations["data"] = 2
    assert [o["action_id"] for o in fallback(state, workflow)] == ["count_target"]
