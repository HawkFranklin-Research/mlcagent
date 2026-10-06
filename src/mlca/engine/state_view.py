from typing import Any


def build(state: Any, workflow: Any) -> Any:
    event = workflow.events[state.current_event]
    latest = next((s for s in reversed(state.steps) if s["status"] == "completed"), None)
    return {
        "event": event.model_dump(),
        "actions": {a: workflow.actions[a].model_dump() for a in event.actions},
        "subgoals": {k: v for k, v in state.subgoals.items() if k.startswith(event.id + ".")},
        "facts": {
            k: {"value": v["value"], "unit": v.get("unit"), "source": v["source"], "sha256": v["sha256"]}
            for k, v in state.facts.items()
        },
        "inventory": state.inventory,
        "brief": state.brief,
        "columns": state.columns,
        "last_observation": {"outputs": latest.get("outputs", []), "metrics": latest.get("metrics", [])}
        if latest
        else {},
        "artifact_names": list(state.artefacts),
        "test_unlocked": state.test_unlocked,
    }
