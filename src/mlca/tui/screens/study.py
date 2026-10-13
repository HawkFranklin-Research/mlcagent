from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static


class StudyScreen(ModalScreen[dict | None]):
    CSS = """StudyScreen { align: center middle; }
    #study-form { width: 90%; max-width: 120; height: 90%; overflow-y: auto; border: round $accent; padding: 1 2; }
    #study-buttons { height: 3; } Input, Select { margin-bottom: 1; }
    .study-why { color: $text-muted; margin-bottom: 1; } #study-error { color: $error; height: auto; }
    #study-draft { color: $accent; height: auto; margin-bottom: 1; }"""

    def __init__(self, state, proposed=None, drafter=None):
        super().__init__()
        self.drafter = drafter
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
            yield Static("[b]Study details[/b] · MLCA drafts, you save")
            yield Static("", id="study-draft")
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
        if self.drafter:
            self.query_one("#study-draft", Static).update(
                "✦ AI is drafting the brief from the column summary…"
            )
            self.request_draft(self.query_one("#study-primary", Select).value)

    def snapshot(self):
        values = {f: self.query_one("#study-" + f, Input).value for f in ["aim", "unit"]}
        values.update({s.id.removeprefix("study-"): s.value for s in self.query(Select)})
        return values

    @work(thread=True, exclusive=True)
    def request_draft(self, primary):
        before = self.app.call_from_thread(self.snapshot)
        try:
            draft, error = self.drafter(primary), None
        except Exception as exc:
            draft, error = None, str(exc)
        self.app.call_from_thread(self.apply_draft, draft, error, before)

    def apply_draft(self, draft, error, before):
        if not self.is_mounted:
            return
        note = self.query_one("#study-draft", Static)
        if not draft:
            note.update(
                "AI draft unavailable"
                + (": " + error[:120] if error else "")
                + ". Column suggestions use local rules."
            )
            return
        now = self.snapshot()
        filled = []
        for field in ["aim", "unit"]:
            if draft.get(field) and now[field] == before[field]:
                self.query_one("#study-" + field, Input).value = draft[field]
                filled.append(field)
        for field in ["target", "duration", "event_column"]:
            if draft.get(field) and field in now and now[field] == before[field]:
                select = self.query_one("#study-" + field, Select)
                select.value = draft[field]
                self.query_one("#study-why-" + field, Static).update("✦ AI draft: " + draft[field])
                filled.append(field)
        repeated = {"yes": "yes", "no": "no"}.get(str(draft.get("repeated", "")).lower())
        if repeated and now.get("repeated_subjects") == before.get("repeated_subjects"):
            self.query_one("#study-repeated_subjects", Select).value = repeated
        note.update(
            "✦ Drafted by AI: check it, edit anything wrong, then Save."
            if filled
            else "AI draft added nothing new."
        )

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
