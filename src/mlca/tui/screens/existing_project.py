from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class ExistingProjectScreen(ModalScreen[str | None]):
    CSS = """ExistingProjectScreen { align: center middle; }
    #existing-project { width: 90%; max-width: 100; height: auto; max-height: 90%;
        padding: 1 2; border: round $accent; overflow-y: auto; }
    #existing-project Button { width: 100%; margin-top: 1; }"""

    def __init__(self, path):
        super().__init__()
        self.path = path

    def compose(self) -> ComposeResult:
        with Vertical(id="existing-project"):
            yield Static("This folder already contains an MLCA study or an earlier initialization attempt.")
            yield Static(str(self.path), markup=False)
            yield Static(
                "Open it to continue if possible, or start a fresh study in a new study-NNN subfolder. The previous attempt's files and logs are kept. Your new-study form is retained for the fresh attempt."
            )
            yield Button(
                "Open existing study",
                id="existing-open",
                disabled=not (self.path / ".mlca/project.yaml").is_file(),
            )
            yield Button("Create fresh study in a new subfolder", id="existing-fresh", variant="primary")
            yield Button("Cancel", id="existing-cancel")

    def on_button_pressed(self, event):
        self.dismiss({"existing-open": "open", "existing-fresh": "fresh"}.get(event.button.id))
