from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static


class StudyScreen(ModalScreen[dict | None]):
    CSS = """StudyScreen { align: center middle; }
    #study-form { width: 90%; max-width: 120; height: 90%; overflow-y: auto; border: round $accent; padding: 1 2; }
    #study-buttons { height: 3; } Input, Select { margin-bottom: 1; }"""

    def __init__(self, state):
        super().__init__()
        self.state = state

    def compose(self) -> ComposeResult:
        with Vertical(id="study-form"):
            yield Static("Resolve study details — actual column names only; no automatic target selection")
            yield Label("Main study table")
            yield Select(
                [(n, n) for n in self.state.data],
                value=self.state.primary_data or next(iter(self.state.data)),
                id="study-primary",
            )
            yield Label("Study aim")
            yield Input(self.state.brief.get("aim", ""), id="study-aim")
            for field, label in [
                ("target", "Column to predict"),
                ("duration", "Time until event or last follow-up"),
                ("event_column", "Whether the event happened (1) or was censored (0)"),
            ]:
                if (field == "target" and self.state.template_id == "survival") or (
                    field != "target" and self.state.template_id != "survival"
                ):
                    continue
                yield Label(label)
                yield Select([], id="study-" + field, prompt="Choose a column")
            yield Label("What does one row represent? Patient, visit, sample…")
            yield Input(self.state.brief.get("unit", ""), id="study-unit")
            yield Label("Can one subject appear in several rows?")
            yield Select(
                [("Not sure yet", "unknown"), ("Yes", "yes"), ("No", "no")],
                value=self.state.brief.get("repeated_subjects", "unknown"),
                id="study-repeated_subjects",
            )
            with Horizontal(id="study-buttons"):
                yield Button("Save study details", id="study-save", variant="primary")
                yield Button("Cancel", id="study-cancel")

    def on_mount(self):
        self.update_columns()

    def on_select_changed(self, event):
        if event.select.id == "study-primary":
            self.update_columns()

    def update_columns(self):
        name = self.query_one("#study-primary", Select).value
        if name not in self.state.data:
            return
        columns = next(i["columns"] for i in self.state.inventory if i["name"] == name)
        for select in self.query(Select):
            field = select.id.removeprefix("study-")
            if field not in {"target", "duration", "event_column"}:
                continue
            select.set_options([("I'll decide later", ""), *[(c, c) for c in columns]])
            value = self.state.columns.get(field)
            select.value = value if value in columns else ""

    def on_button_pressed(self, event):
        if event.button.id == "study-cancel":
            self.dismiss(None)
        elif event.button.id == "study-save":
            answers = {field: self.query_one("#study-" + field, Input).value for field in ["aim", "unit"]}
            for select in self.query(Select):
                field = select.id.removeprefix("study-")
                if field != "primary":
                    answers[field] = select.value or ""
            if self.state.template_id == "survival":
                answers["target"] = answers["duration"]
            self.dismiss({"answers": answers, "primary_data": self.query_one("#study-primary", Select).value})
