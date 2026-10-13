from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, Static

WHITE, BODY, MUTED, BLUE, AMBER = "#f2f5f8", "#c7d0d9", "#8a96a3", "#5fb4f0", "#f0c040"


def short(value, limit=110):
    value = " ".join(str(value or "").split())
    return value if len(value) <= limit else value[: limit - 1] + "…"


def card_text(number, option):
    title = " ".join(option["title"].split()[:8])
    text = Text()
    text.append(f" {number} ", style=f"bold reverse {AMBER if option.get('locked') else BLUE}")
    text.append("  " + title, style=f"bold {MUTED if option.get('disabled') else WHITE}")
    if option.get("source") == "agent":
        text.append("   ✦ suggested by AI", style=BLUE)
    text.append("\n")
    if option.get("description"):
        text.append(
            "     " + short(option["description"]) + "\n", style=MUTED if option.get("disabled") else BODY
        )
    produces = option.get("produces")
    if produces:
        text.append("     • Produces: " + short(produces, 90) + "\n", style=MUTED)
    why = option.get("why_now")
    if why and option.get("source") == "agent":
        text.append("     • Why now: " + short(why, 90) + "\n", style=MUTED)
    if option.get("est_cost_usd") is not None:
        text.append(f"     • Cost: ≤ ${option['est_cost_usd']:.4f}\n", style=MUTED)
    return text


class OptionCard(Button):
    DEFAULT_CSS = """OptionCard { width: 100%; height: auto; min-height: 3; margin-bottom: 1; padding: 0 2;
        border: round $primary-darken-2; background: $panel; text-align: left; content-align: left top; }
    OptionCard:focus { border: round $accent; background: $boost; text-style: none; }
    OptionCard:hover { border: round $primary; }
    OptionCard.-disabled { opacity: 70%; border: round $panel-lighten-1; }"""

    def __init__(self, number, option):
        self.option_id = option["id"]
        super().__init__(
            card_text(number, option), id=f"option-{number}", disabled=option.get("disabled", False)
        )


def hint_for(options):
    ids = {o["id"] for o in options}
    if "ui:connect" in ids:
        return "No AI model connected yet. Built-in steps still work."
    if "human:study" in ids:
        return "Next, choose what to predict and what one row represents."
    if "next" in ids:
        return "This step is complete. Continue, or run an optional extra."
    return "Choose a card to continue."


class Options(Vertical):
    class Selected(Message):
        def __init__(self, option_id):
            super().__init__()
            self.option_id = option_id

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items = []

    def compose(self) -> ComposeResult:
        yield Static("Preparing your choices…", id="options-hint", markup=False)

    async def render_options(self, options):
        self.items = options
        await self.query(OptionCard).remove()
        self.query_one("#options-hint", Static).update(Text(hint_for(options), style=f"bold {AMBER}"))
        await self.mount(*(OptionCard(i, o) for i, o in enumerate(options, 1)))
        self.app.refresh_bindings()

    def on_button_pressed(self, event):
        if isinstance(event.button, OptionCard):
            event.stop()
            self.post_message(self.Selected(event.button.option_id))

    def on_key(self, event):
        if event.key in {"up", "down"}:
            buttons = list(self.query(OptionCard))
            if buttons:
                index = buttons.index(self.app.focused) if self.app.focused in buttons else -1
                buttons[(index + (1 if event.key == "down" else -1)) % len(buttons)].focus()
                event.stop()
