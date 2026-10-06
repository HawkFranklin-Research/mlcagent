from typing import Any

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from mlca.tui.banner import brand_line

from ..widgets.event_graph import EventGraph
from ..widgets.facts import Facts
from ..widgets.log_stream import LogStream
from ..widgets.options import Options
from ..widgets.status_bar import StatusBar
from ..widgets.subgoals import Subgoals


class MainScreen(Screen):
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
