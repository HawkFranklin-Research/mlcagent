from textual.widgets import Static
from mlca.ui_text import text


class EventGraph(Static):
    def render_state(self,status):
        state=status['event_statuses']
        lines=[text('events'),'']
        for event in status['workflow']['events']:
            symbol='✓' if state.get(event)=='done' else '→' if event==status['current_event'] else '·'
            lines.append(f'{symbol} {event}')
        self.update('\n'.join(lines))
