from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from ..widgets.event_graph import EventGraph
from ..widgets.subgoals import Subgoals
from ..widgets.options import Options
from ..widgets.facts import Facts
from ..widgets.log_stream import LogStream
from ..widgets.status_bar import StatusBar


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id='panels'):
            yield EventGraph(id='event-graph')
            with Vertical(id='center'):
                yield Subgoals(id='subgoals')
                yield Options(id='options')
            yield Facts(id='facts')
        yield LogStream(id='log-stream')
        yield StatusBar(id='status-bar')
        yield Footer()

    def on_mount(self):
        self.app.refresh_project()
