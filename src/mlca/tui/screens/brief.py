from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static

from mlca.ui_text import text


class FormScreen(ModalScreen[dict | None]):
    CSS = """FormScreen { align: center middle; } #form { width: 80%; height: auto; max-height: 90%; border: round $accent; padding: 1 2; overflow-y: auto; } Input { margin-bottom: 1; }"""

    def __init__(self, title: str, fields: list[tuple[str, str, str]]) -> None:
        super().__init__()
        self.form_title = title
        self.fields = fields

    def compose(self) -> ComposeResult:
        with Vertical(id="form"):
            yield Static(self.form_title)
            for identifier, label, value in self.fields:
                yield Label(label)
                yield Input(value=value, id=identifier)
            with Horizontal():
                yield Button(text("submit"), id="submit", variant="primary")
                yield Button(text("cancel"), id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> Any:
        if event.button.id == "cancel":
            self.dismiss(None)
        elif event.button.id == "submit":
            self.dismiss(
                {
                    identifier: self.query_one("#" + identifier, Input).value
                    for identifier, _, _ in self.fields
                }
            )
