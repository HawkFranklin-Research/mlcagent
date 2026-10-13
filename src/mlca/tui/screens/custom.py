import re

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

PROCEED = re.compile(
    r"(?i)^\s*(just\s+|please\s+)?(proceed|continue|go ahead|carry on|move on|next)\b"
    r"|\b(complete|finish|do)\s+(the\s+|this\s+)?(setup|step|it|everything|what you can)\b"
)
EXPLAIN = re.compile(r"(?i)^\s*(explain|help|what (do|does|should|is)|why)\b")


def intent(text):
    """Local routing before any model call: 'proceed', 'explain' or None (a real instruction)."""
    if PROCEED.search(text):
        return "proceed"
    if EXPLAIN.search(text):
        return "explain"
    return None


class CustomScreen(ModalScreen[dict | None]):
    BINDINGS = [("escape", "cancel", "Cancel")]
    CSS = """CustomScreen { align: center middle; }
    #custom { width: 80%; height: auto; max-height: 90%; border: round $accent; padding: 1 2; overflow-y: auto; }
    #custom-scope { color: $text-muted; margin-bottom: 1; }
    .suggestion { width: 100%; height: 1; min-width: 0; border: none; margin: 0; padding: 0 1;
        text-align: left; content-align: left middle; background: $panel; }
    .suggestion:focus, .suggestion:hover { background: $boost; text-style: bold; }
    #custom-input { margin-top: 1; } #custom-buttons { height: 3; margin-top: 1; }"""

    def __init__(self, scope, suggestions):
        super().__init__()
        self.scope = scope
        self.suggestions = suggestions

    def compose(self) -> ComposeResult:
        with Vertical(id="custom"):
            yield Static("[b]Ask MLCA[/b]")
            yield Static("Allowed in this step: " + self.scope, id="custom-scope")
            yield Label("Suggestions (click to use)")
            for number, item in enumerate(self.suggestions):
                yield Button("› " + item, id=f"suggestion-{number}", classes="suggestion")
            yield Input(placeholder="Or type your own instruction", id="custom-input")
            with Horizontal(id="custom-buttons"):
                yield Button("Run", id="custom-run", variant="primary")
                yield Button("Cancel", id="custom-cancel")

    def action_cancel(self):
        self.dismiss(None)

    def on_input_submitted(self, event):
        self.submit()

    def submit(self):
        value = self.query_one("#custom-input", Input).value.strip()
        if value:
            self.dismiss({"instruction": value})

    def on_button_pressed(self, event):
        identifier = event.button.id or ""
        if identifier.startswith("suggestion-"):
            self.dismiss({"instruction": self.suggestions[int(identifier.removeprefix("suggestion-"))]})
        elif identifier == "custom-run":
            self.submit()
        elif identifier == "custom-cancel":
            self.dismiss(None)
