from textual.screen import Screen
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.widgets import Static,Button,Header,Footer
from mlca.paths import resource
from mlca.ui_text import text
from mlca import __version__


class WelcomeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Static((resource('assets')/'banner.txt').read_text(),markup=False)
            yield Static(f'{text("title")} {__version__}')
            yield Static(text('first_run'))
            with Horizontal():
                yield Button(text('open'),id='open')
                yield Button(text('init'),id='init',variant='primary')
                yield Button(text('configure'),id='configure')
                yield Button(text('quit'),id='quit')
        yield Footer()

    def on_button_pressed(self,event):
        getattr(self.app,'action_'+event.button.id)()
