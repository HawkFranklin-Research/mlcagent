from typing import Any


def build(state: Any) -> Any:
    return [
        {"step_id": s["step_id"], **figure}
        for s in state.steps
        if s["status"] == "completed"
        for figure in s.get("figures", [])
    ]
