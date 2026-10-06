from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from mlca.tui.banner import brand_line
from mlca.ui_text import text

from ..widgets.event_graph import EventGraph
from ..widgets.facts import Facts
from ..widgets.log_stream import LogStream
from ..widgets.options import Options
from ..widgets.status_bar import StatusBar
from ..widgets.subgoals import Subgoals


class MainScreen(Screen):
    BINDINGS = [
        (key, "app." + action, text(label))
        for key, action, label in [
            ("1", "choose_1", "choose"),
            ("2", "choose_2", "choose"),
            ("3", "choose_3", "choose"),
            ("4", "choose_4", "choose"),
            ("n", "next", "next"),
            ("l", "loop", "loop"),
            ("c", "custom", "custom"),
            ("f", "confirm", "confirm"),
            ("b", "branches", "branches"),
            ("r", "report", "report"),
            ("u", "usage", "usage"),
            ("v", "view_figure", "view_figure"),
            ("t", "unlock", "unlock"),
            ("o", "open", "open"),
            ("s", "configure", "configure"),
            ("q", "quit", "quit"),
        ]
    ]
    DEFAULT_CSS = "MainScreen #brand { height: 1; margin-bottom: 1; }"

    def compose(self) -> ComposeResult:
        yield Static(brand_line(getattr(self.app, "project", None)), id="brand")
        with Horizontal(id="panels"):
            yield EventGraph(id="event-graph")
            with Vertical(id="center"):
                yield Subgoals(id="subgoals")
                yield Options(id="options")
            yield Facts(id="facts")
        yield LogStream(id="log-stream")
        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> Any:
        self.app.refresh_project()
