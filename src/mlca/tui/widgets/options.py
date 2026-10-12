from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, Static


class OptionCard(Button):
    DEFAULT_CSS = "OptionCard { width: 100%; height: auto; min-height: 5; margin-bottom: 1; padding: 0 1; border: round $primary; text-align: left; }"

    def __init__(self, number, option):
        self.option_id = option["id"]
        title = " ".join(option["title"].split()[:8])

        def short(value):
            value = " ".join(value.split())
            return value if len(value) <= 95 else value[:92] + "…"

        lines = [
            f"{number}. {title}  ·  {option.get('source', 'template')}",
            short(option.get("description", "")),
            "Produces: " + short(option.get("produces", "Recorded outputs")),
            "Why now: " + short(option.get("why_now", "")),
        ]
        if option.get("est_cost_usd") is not None:
            lines.append(f"Estimated request cost ≤ ${option['est_cost_usd']:.4f}")
        super().__init__(
            Text("\n".join(lines)),
            id=f"option-{number}",
            tooltip=Text(
                option.get("description", "")
                + "\nProduces: "
                + option.get("produces", "")
                + "\nWhy now: "
                + option.get("why_now", "")
            ),
        )


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
        hint = (
            "Inventory recorded. Next, choose what to predict and what one row represents."
            if any(o["id"] == "human:study" for o in options)
            else "Choose a card to continue. Custom instructions must stay within this event."
        )
        self.query_one("#options-hint", Static).update(hint)
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
