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
