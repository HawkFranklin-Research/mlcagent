"""Activity panel: what happened, left to right, and what to do next."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static

from mlca.ui_text import next_hint, record_message

GREEN, AMBER, RED, BLUE, GREY = "#5fd068", "#f0c040", "#ff6b6b", "#5fb4f0", "#7a8591"
LIMIT = 14


def colour(message):
    if message.startswith("✓"):
        return GREEN
    if message.startswith("⚠"):
        return AMBER
    if message.startswith("✗"):
        return RED
    return BLUE


def flow(records):
    """Plain-language messages, oldest left; consecutive repeats collapsed."""
    items = []
    for record in records:
        for line in (record_message(record) or "").splitlines():
            if line and (not items or items[-1] != line):
                items.append(line)
    return items[-LIMIT:]


def render_flow(items):
    result = Text()
    if not items:
        return Text("Nothing has happened yet.", style=GREY)
    for index, item in enumerate(items):
        if index:
            result.append("  →  ", style=GREY)
        result.append(item, style=f"bold {colour(item)}" if index == len(items) - 1 else colour(item))
    return result


class Journey(VerticalScroll):
    DEFAULT_CSS = """Journey { height: auto; max-height: 9; border: round $primary; padding: 0 1; }
    Journey #journey-flow { height: auto; } Journey #journey-next { height: auto; margin-top: 1; }"""

    def compose(self) -> ComposeResult:
        yield Static("", id="journey-flow")
        yield Static("", id="journey-next")

    def render_state(self, status, records, workflow):
        self.query_one("#journey-flow", Static).update(render_flow(flow(records)))
        hint = next_hint(status)
        self.query_one("#journey-next", Static).update(
            Text.assemble(("Next: ", "bold #f0c040"), (hint, "#f2f5f8")) if hint else ""
        )
        self.scroll_end(animate=False)
