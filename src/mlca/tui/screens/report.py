from typing import Any

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

from mlca.ui_text import text


class ReportScreen(ModalScreen):
    def __init__(self, content: Any) -> None:
        super().__init__()
        self.content = content

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Markdown(self.content)
            yield Button(text("cancel"), id="close-report")

    def on_button_pressed(self, event: Any) -> Any:
        self.dismiss()
