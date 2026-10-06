from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.widgets import OptionList
from mlca.templates.registry import available


class TemplatePickScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        self.names=list(available())
        yield OptionList(*self.names)

    def on_option_list_option_selected(self,event):
        self.dismiss(self.names[event.option_index])
