from typing import Any

from rich.text import Text
from textual.widgets import Static

from mlca.ui_text import missing_study_fields

GREEN, YELLOW, GREY, WHITE = "#5fd068", "#f0c040", "#8a96a3", "#f2f5f8"


class Subgoals(Static):
    def render_state(self, status: Any) -> Any:
        event = status["event_spec"]
        title = status.get("event_titles", {}).get(event["id"], event.get("title", event["id"]))
        lines = Text()
        lines.append(title + "\n", style=f"bold {WHITE}")
        lines.append(event["goal"] + "\n\n", style=GREY)
        for subgoal in event["subgoals"]:
            result = status["subgoals"].get(event["id"] + "." + subgoal["id"], {})
            if result.get("passed"):
                lines.append("✓ " + subgoal["text"] + "\n", style=GREEN)
                continue
            lines.append("○ " + subgoal["text"] + "\n", style=YELLOW)
            if subgoal["check"]["type"] == "study_fields_resolved":
                missing = missing_study_fields(result.get("detail") or status.get("study_detail", ""))
                if missing:
                    lines.append("    still missing: " + missing + "\n", style=GREY)
        self.update(lines)
