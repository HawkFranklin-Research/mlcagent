from typing import Any

from textual.widgets import Static

from mlca.ui_text import text


class Options(Static):
    def render_options(self, options: Any) -> Any:
        self.update(
            text("options")
            + "\n\n"
            + "\n".join(f"{o['id']}. {o['title']}\n   {o.get('note', o.get('why_now', ''))}" for o in options)
        )
