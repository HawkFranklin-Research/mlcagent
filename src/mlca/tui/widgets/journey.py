from textual.app import ComposeResult
from textual.containers import HorizontalScroll, Vertical
from textual.widgets import RichLog, Static

from mlca.ui_text import record_message


def strip(status):
    return " → ".join(
        event
        + " "
        + (
            "●"
            if event == status["current_event"]
            else "✓"
            if status["event_statuses"].get(event) == "done"
            else "🔒"
            if event == "split" or status["event_statuses"].get(event) == "locked"
            else "·"
        )
        for event in status["workflow"]["events"]
    )


def trail(records, workflow):
    steps, items = {}, []
    for record in records:
        kind, p = record.type.value, record.payload
        if kind == "StepStarted":
            action = workflow.actions.get(p["action_id"])
            items.append([action.title if action else "Custom instruction", "⏳"])
            steps[p["step_id"]] = items[-1]
        elif kind in {"StepCompleted", "StepFailed"} and p["step_id"] in steps:
            steps[p["step_id"]][1] = "✓" if kind == "StepCompleted" else "⚠"
        elif kind == "StudyFieldsResolved":
            items.append(["Choose target (you)", "✓"])
        elif kind == "UserConfirmed":
            items.append(["Confirm brief (you)", "✓"])
        elif kind == "TestUnlocked":
            items.append(["Approve test (you)", "✓"])
    return " → ".join(" ".join(item) for item in items) or "No recorded actions yet"


class Journey(Vertical):
    DEFAULT_CSS = """Journey { height: 1fr; min-height: 5; border: round $primary; }
    Journey HorizontalScroll { height: 1; } Journey Static { width: auto; height: 1; }
    Journey RichLog { height: 1fr; }"""

    def compose(self) -> ComposeResult:
        with HorizontalScroll():
            yield Static("", id="journey-strip", markup=False)
        with HorizontalScroll():
            yield Static("", id="journey-trail", markup=False)
        yield RichLog(id="journey-messages", markup=False, highlight=False, wrap=True)

    def render_state(self, status, records, workflow):
        self.query_one("#journey-strip", Static).update(strip(status))
        self.query_one("#journey-trail", Static).update(trail(records, workflow))
        log = self.query_one(RichLog)
        log.clear()
        for record in records[-150:]:
            message = record_message(record)
            if message:
                log.write(message)
        if status["current_event"] == "onboard" and not status["columns"].get("target"):
            log.write("⚠ Target column not chosen yet: select the Choose target card.")
