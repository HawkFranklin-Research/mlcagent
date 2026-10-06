from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from mlca import __version__
from mlca.paths import resource
from mlca.ui_text import text


class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static((resource("assets") / "banner.txt").read_text(), markup=False)
            yield Static(f"{text('title')} {__version__}")
            yield Static(text("first_run"))
            with Horizontal():
                yield Button(text("open"), id="open")
                yield Button(text("init"), id="init", variant="primary")
                yield Button(text("configure"), id="configure")
                yield Button(text("quit"), id="quit")
        yield Footer()

    def on_button_pressed(self, event: Any) -> Any:
        getattr(self.app, "action_" + event.button.id)()
