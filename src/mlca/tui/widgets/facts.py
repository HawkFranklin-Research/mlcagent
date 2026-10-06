from textual.widgets import Static
from mlca.ui_text import text


class Facts(Static):
    def render_state(self,status):
        self.update(text('facts')+'\n\n'+'\n'.join(f'{key}: {fact["value"]}' for key,fact in status['facts'].items()))
