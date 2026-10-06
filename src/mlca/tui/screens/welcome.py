from typing import Any

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from mlca.tui.banner import banner
from mlca.ui_text import text


class WelcomeScreen(Screen):
    BINDINGS = [
        ("o", "app.open", text("open")),
        ("i", "app.init", text("init")),
        ("s", "app.configure", text("configure")),
        ("q", "app.quit", text("quit")),
    ]
    DEFAULT_CSS = """
    WelcomeScreen { align: center middle; }
    WelcomeScreen #welcome { width: auto; height: auto; padding: 1 2; }
    WelcomeScreen #banner { width: auto; margin-bottom: 1; }
    WelcomeScreen #hint { color: $text-muted; margin-bottom: 1; }
    WelcomeScreen #actions { width: auto; height: auto; }
    WelcomeScreen #actions Button { margin-right: 1; min-width: 12; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="welcome"):
            yield Static(banner(self.app.size.width, getattr(self.app, "project", None)), id="banner")
            yield Static(text("first_run"), id="hint")
            with Center():
                with Horizontal(id="actions"):
                    yield Button(text("open"), id="open")
                    yield Button(text("init"), id="init", variant="primary")
                    yield Button(text("configure"), id="configure")
                    yield Button(text("quit"), id="quit")
        yield Footer()

    def on_resize(self, event: Any) -> None:
        self.query_one("#banner", Static).update(banner(event.size.width, getattr(self.app, "project", None)))

    def on_button_pressed(self, event: Any) -> Any:
        getattr(self.app, "action_" + event.button.id)()
