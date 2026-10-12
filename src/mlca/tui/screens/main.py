from typing import Any

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Static

from mlca.tui.banner import brand_line

from ..widgets.event_graph import EventGraph
from ..widgets.facts import Facts
from ..widgets.log_stream import LogStream
from ..widgets.options import Options
from ..widgets.progress import Progress
from ..widgets.status_bar import StatusBar
from ..widgets.subgoals import Subgoals


class MainScreen(Screen):
    BINDINGS = [
        *[(str(i), f"app.select_card({i})", f"Card {i}") for i in range(1, 10)],
        ("m", "app.configure", "Models"),
        Binding("s", "app.configure", "Models", show=False),
        ("r", "app.report", "Reports"),
        ("q", "app.quit", "Quit"),
        Binding("d", "app.study", "Study details", show=False),
        Binding("a", "app.approvals", "Approvals", show=False),
        Binding("n", "app.next", "Next", show=False),
        Binding("c", "app.custom", "Custom", show=False),
        Binding("f", "app.confirm", "Confirm", show=False),
        Binding("t", "app.unlock", "Unlock", show=False),
        Binding("b", "app.branches", "Branches", show=False),
        Binding("u", "app.usage", "Usage", show=False),
        Binding("v", "app.view_figure", "Figure", show=False),
        Binding("o", "app.open", "Open", show=False),
        Binding("l", "app.loop", "Loop", show=False),
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
        yield Progress(id="progress")
        yield Static("", id="approvals-banner")
        yield LogStream(id="log-stream")
        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> Any:
        self.app.refresh_project()
