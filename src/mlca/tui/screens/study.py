from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static


class StudyScreen(ModalScreen[dict | None]):
    CSS = """StudyScreen { align: center middle; }
    #study-form { width: 90%; max-width: 120; height: 90%; overflow-y: auto; border: round $accent; padding: 1 2; }
    #study-buttons { height: 3; } Input, Select { margin-bottom: 1; }
    .study-why { color: $text-muted; margin-bottom: 1; } #study-error { color: $error; height: auto; }"""

    def __init__(self, state, proposed=None):
        super().__init__()
        self.confirm_partial = False
        self.suggestions = {}
        self.state = state.model_copy(deep=True)
        if proposed:
            self.state.brief.update({k: v for k, v in proposed.items() if k != "primary_data"})
            self.state.primary_data = proposed.get("primary_data", state.primary_data)
            from mlca.project.init import resolve_columns

            self.state.columns = resolve_columns(
                self.state.brief,
                [i for i in state.inventory if i["name"] == self.state.primary_data],
                state.template_id,
            )

    def compose(self) -> ComposeResult:
        with Vertical(id="study-form"):
            yield Static("[b]Study details[/b] · MLCA suggests, you decide")
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
                yield Static("", id="study-why-" + field, classes="study-why")
            yield Label("What does one row represent? (e.g. one patient, one visit, one sample)")
            yield Input(self.state.brief.get("unit", ""), id="study-unit")
            yield Label("Can one subject appear in several rows?")
            yield Select(
                [("Not sure yet", "unknown"), ("Yes", "yes"), ("No", "no")],
                value=self.state.brief.get("repeated_subjects", "unknown"),
                id="study-repeated_subjects",
            )
            yield Static("", id="study-error")
            with Horizontal(id="study-buttons"):
                yield Button("Save study details", id="study-save", variant="primary")
                yield Button("Cancel", id="study-cancel")

    def on_mount(self):
        self.update_columns()

    def on_select_changed(self, event):
        if event.select.id == "study-primary":
            self.update_columns()

    def load_suggestions(self, name):
        """Local rule-based ranking of the table's columns; nothing is sent anywhere."""
        try:
            from pathlib import Path

            from mlca.engine.suggest import recommendations
            from mlca.project.inventory import read_table

            frame = read_table(Path(self.state.data[name]["original_path"]))
            return recommendations(frame, self.state.template_id)
        except Exception:
            return {}

    def update_columns(self):
        name = self.query_one("#study-primary", Select).value
        if name not in self.state.data:
            return
        columns = next(i["columns"] for i in self.state.inventory if i["name"] == name)
        self.suggestions = self.load_suggestions(name)
        for select in self.query(Select):
            field = select.id.removeprefix("study-")
            if field not in {"target", "duration", "event_column"}:
                continue
            ranked = [c for c in self.suggestions.get(field, []) if c[0] in columns]
            top = ranked[0] if ranked else None
            choices = []
            if top:
                choices.append(("★ " + top[0] + " — recommended", top[0]))
            choices.append(("I'll decide later", ""))
            choices += [(c, c) for c in columns if not top or c != top[0]]
            select.set_options(choices)
            value = self.state.columns.get(field)
            select.value = value if value in columns else (top[0] if top else "")
            why = self.query_one("#study-why-" + field, Static)
            why.update(
                "Recommended: " + top[0] + " (" + ", ".join(top[2]) + ")"
                if top
                else "No clear candidate; choose one."
            )

    def on_button_pressed(self, event):
        if event.button.id == "study-cancel":
            self.dismiss(None)
        elif event.button.id == "study-save":
            answers = {field: self.query_one("#study-" + field, Input).value for field in ["aim", "unit"]}
            for select in self.query(Select):
                field = select.id.removeprefix("study-")
                if field != "primary":
                    answers[field] = select.value if isinstance(select.value, str) else ""
            if self.state.template_id == "survival":
                answers["target"] = answers["duration"]
            labels = {
                "target": "the column to predict",
                "duration": "the time column",
                "event_column": "the event column",
                "unit": "what one row represents",
            }
            needed = ["duration", "event_column"] if self.state.template_id == "survival" else ["target"]
            missing = [labels[f] for f in needed + ["unit"] if not str(answers.get(f, "")).strip()]
            if missing and not self.confirm_partial:
                self.confirm_partial = True
                self.query_one("#study-error", Static).update(
                    "Still needed: "
                    + ", ".join(missing)
                    + ". Fill them in, or press Save again to save a draft."
                )
                return
            self.dismiss({"answers": answers, "primary_data": self.query_one("#study-primary", Select).value})
