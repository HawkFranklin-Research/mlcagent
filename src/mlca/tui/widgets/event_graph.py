from typing import Any

from rich.text import Text
from textual.widgets import Static

from mlca.ui_text import text

GREEN, YELLOW, RED, GREY = "#5fd068", "#f0c040", "#ff6b6b", "#7a8591"


def event_state(status: Any, event: str) -> str:
    if event in status.get("failed_events", set()):
        return "failed"
    if event == status["current_event"]:
        return "current"
    state = status["event_statuses"].get(event)
    if state == "done":
        return "done"
    if state == "locked" or (event == "test" and not status.get("test_unlocked")):
        return "locked"
    return "ahead"


MARKS = {
    "done": ("✓", GREEN),
    "current": ("●", YELLOW),
    "failed": ("✗", RED),
    "locked": ("🔒", GREY),
    "ahead": ("·", GREY),
}


class EventGraph(Static):
    def render_state(self, status: Any) -> Any:
        titles = status.get("event_titles", {})
        lines = Text(text("events") + "\n\n", style="bold")
        for event in status["workflow"]["events"]:
            state = event_state(status, event)
            mark, colour = MARKS[state]
            style = f"bold {colour}" if state in {"current", "failed"} else colour
            lines.append(f"{mark} {titles.get(event, event)}\n", style=style)
        self.update(lines)
