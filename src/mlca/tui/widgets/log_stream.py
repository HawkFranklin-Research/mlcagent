from typing import Any

from textual.widgets import RichLog


class LogStream(RichLog):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(markup=False, highlight=False, wrap=True, **kwargs)


def result_summary(method: str, result: Any) -> str:
    if method == "options":
        return "options: " + " · ".join(
            item["id"] if item["id"] == "custom" else item["id"] + " " + item["title"] for item in result
        )
    if isinstance(result, dict):
        parts = [
            f"{key}: {result[key]}"
            for key in ("step_id", "decision", "reason", "event", "entered", "complete")
            if key in result
        ]
        return method + ": " + (" · ".join(parts) or "completed")
    return method + ": completed"


def record_summary(record: Any) -> str:
    payload = record.payload
    parts = [
        str(payload[key])
        for key in (
            "action_id",
            "event_id",
            "step_id",
            "subgoal_id",
            "decision",
            "reason",
            "note",
            "text",
            "client",
            "name",
        )
        if key in payload
    ]
    if "options" in payload:
        parts.append(f"{len(payload['options'])} options")
    if "outputs" in payload:
        parts.append(f"{len(payload['outputs'])} outputs")
    if "passed" in payload:
        parts.append("passed" if payload["passed"] else "pending")
    if "exit_status" in payload:
        parts.append("exit " + str(payload["exit_status"]))
    return record.type.value + (": " + " · ".join(parts)[:180] if parts else "")
