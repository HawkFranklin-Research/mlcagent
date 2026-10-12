from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Label, Select, Static

from mlca.project.discovery import discover, registrations
from mlca.templates.registry import available, get

from .file_picker import FilePicker


class ProjectScreen(ModalScreen[dict | None]):
    CSS = """ProjectScreen { align: center middle; }
    #project-form { width: 90%; max-width: 120; height: 90%; border: round $accent; padding: 1 2; overflow-y: auto; }
    Input, Select { margin-bottom: 1; } .path-row { height: 3; margin-bottom: 1; }
    .path-row Input { width: 1fr; } .path-row Button { width: 12; }
    #project-buttons { height: 3; }"""

    def __init__(self, path, initialise=False):
        super().__init__()
        self.path, self.initialise = path, initialise
        self.files = []
        self.tables = {}
        self.columns = []

    def compose(self) -> ComposeResult:
        with Vertical(id="project-form"):
            yield Static("Create a study" if self.initialise else "Open a project")
            yield Label("Project folder")
            with Horizontal(classes="path-row"):
                yield Input(str(self.path), id="path")
                yield Button("Browse", id="browse-project")
            if self.initialise:
                yield Label("Data file or folder — CSV, TSV, Parquet (tables are never merged automatically)")
                with Horizontal(classes="path-row"):
                    yield Input(id="data")
                    yield Button("Browse", id="browse-data")
                yield Button("Find tables", id="find-tables")
                yield Label("Main study table — the split applies only to this table")
                yield Select([], id="primary", prompt="Find tables first")
                yield Static(
                    "Other discovered tables are supporting inputs. Review the list before creating.",
                    id="file-list",
                )
                yield Checkbox(
                    "Register the other discovered tables as supporting inputs",
                    value=False,
                    id="supporting-tables",
                )
                yield Label("Workflow")
                yield Select(
                    [(get(k).spec.title, k) for k in available()],
                    value="tabular_classification",
                    allow_blank=False,
                    id="template",
                )
                yield Label("What do you want to learn or predict?")
                yield Input(id="aim")
                yield Label("Which column do you want to predict?", id="target-label")
                yield Select([("I'll decide later", "")], value="", allow_blank=False, id="target")
                yield Label("Time until the event or last follow-up", id="duration-label")
                yield Select([("I'll decide later", "")], value="", allow_blank=False, id="duration")
                yield Label(
                    "Did the outcome happen? Event column (1 = happened, 0 = censored)", id="event-label"
                )
                yield Select([("I'll decide later", "")], value="", allow_blank=False, id="event_column")
                yield Label(
                    "What does one row represent? Patient, visit, specimen, sample… (optional for now)"
                )
                yield Input(id="unit")
                yield Label("Can the same patient or subject appear in several rows?")
                yield Select(
                    [("Not sure yet", "unknown"), ("Yes", "yes"), ("No", "no")],
                    value="unknown",
                    id="repeated_subjects",
                )
            yield Static("", id="form-error")
            with Horizontal(id="project-buttons"):
                yield Button("Create study" if self.initialise else "Open", id="submit", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self):
        self.template_changed()

    def template_changed(self):
        if not self.initialise:
            return
        survival = self.query_one("#template", Select).value == "survival"
        for identifier in ["duration-label", "duration", "event-label", "event_column"]:
            self.query_one("#" + identifier).display = survival
        for identifier in ["target-label", "target"]:
            self.query_one("#" + identifier).display = not survival

    def find_tables(self):
        try:
            value = self.query_one("#data", Input).value.strip()
            if not value:
                raise ValueError("Choose a data file or folder first")
            self.files = discover([Path(value)])
            self.tables = dict(registrations(self.files))
            self.query_one("#primary", Select).set_options(
                [(f"{name} — {path.name}", name) for name, path in self.tables.items()]
            )
            self.query_one("#primary", Select).value = (
                next(iter(self.tables)) if len(self.tables) == 1 else Select.NULL
            )
            self.query_one("#file-list", Static).update(
                "\n".join(
                    f"{name}: {path} ({path.stat().st_size:,} bytes)" for name, path in self.tables.items()
                )
            )
            self.query_one("#form-error", Static).update("")
        except Exception as exc:
            self.files, self.tables = [], {}
            self.query_one("#form-error", Static).update(str(exc))

    def on_select_changed(self, event):
        if event.select.id == "template":
            self.template_changed()
        elif event.select.id == "primary" and event.value in self.tables:
            try:
                from mlca.project.inventory import table_columns

                self.columns = table_columns(self.tables[event.value])
                for identifier in ["target", "duration", "event_column"]:
                    select = self.query_one("#" + identifier, Select)
                    select.set_options([("I'll decide later", ""), *[(str(c), c) for c in self.columns]])
                    select.value = ""
            except Exception as exc:
                self.query_one("#form-error", Static).update(str(exc))

    def on_button_pressed(self, event):
        identifier = event.button.id
        if identifier == "cancel":
            self.dismiss(None)
        elif identifier in {"browse-project", "browse-data"}:
            field = "path" if identifier == "browse-project" else "data"

            def selected(path):
                if path:
                    self.query_one("#" + field, Input).value = path
                    if field == "data":
                        self.find_tables()

            self.app.push_screen(
                FilePicker(self.query_one("#" + field, Input).value, folders_only=field == "path"), selected
            )
        elif identifier == "find-tables":
            self.find_tables()
        elif identifier == "submit":
            result = {"path": self.query_one("#path", Input).value.strip()}
            if not result["path"]:
                self.query_one("#form-error", Static).update("Choose a project folder first")
                return
            if self.initialise:
                if not self.tables:
                    self.find_tables()
                primary = self.query_one("#primary", Select).value
                if primary not in self.tables:
                    self.query_one("#form-error", Static).update(
                        "Choose the main study table. No files will be combined automatically."
                    )
                    return
                result.update(
                    data=[str(p) for p in self.files]
                    if self.query_one("#supporting-tables", Checkbox).value
                    else [str(self.tables[primary])],
                    primary_data=str(self.tables[primary]),
                    template=self.query_one("#template", Select).value,
                )
                result.update({k: self.query_one("#" + k, Input).value for k in ["aim", "unit"]})
                result.update(
                    {
                        k: self.query_one("#" + k, Select).value
                        if isinstance(self.query_one("#" + k, Select).value, str)
                        else ""
                        for k in ["target", "duration", "event_column", "repeated_subjects"]
                    }
                )
                if result["template"] == "survival":
                    result["target"] = result["duration"]
            self.dismiss(result)
