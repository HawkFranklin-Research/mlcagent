from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import Markdown, Button
from textual.containers import Vertical
from mlca.ui_text import text


class ReportScreen(ModalScreen):
    def __init__(self,content):
        super().__init__()
        self.content=content

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Markdown(self.content)
            yield Button(text('cancel'),id='close-report')

    def on_button_pressed(self,event):
        self.dismiss()
