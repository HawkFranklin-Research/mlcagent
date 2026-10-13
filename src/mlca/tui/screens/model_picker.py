from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, OptionList, Static
from textual.widgets.option_list import Option

from mlca.llm.catalog import cached, fetch


class ModelPicker(ModalScreen[object | None]):
    CSS = """ModelPicker { align: center middle; }
    #models { width: 90%; height: 90%; border: round $accent; padding: 1 2; }
    OptionList { height: 1fr; } #model-buttons { height: 3; }"""

    def __init__(self, provider):
        super().__init__()
        self.provider = provider
        self.models, self.stale = cached(provider)
        try:
            from mlca.config import load

            self.selected = set(load().catalog.selected)
        except Exception:
            self.selected = set()
        self.filtered_models = []

    def compose(self) -> ComposeResult:
        with Vertical(id="models"):
            yield Static("[b]Choose a model[/b]")
            yield Input(placeholder="Search by name or ID", id="model-search")
            yield Checkbox("Free models only", id="free-only")
            yield Static(
                "Loading models…" if not self.models or self.stale else "Models loaded", id="catalog-status"
            )
            yield OptionList(id="model-list")
            with Horizontal(id="model-buttons"):
                yield Button("Refresh", id="refresh-models")
                yield Button("Cancel", id="cancel-models")

    def on_mount(self):
        self.render_models()
        if not self.models or self.stale:
            self.query_one("#refresh-models", Button).disabled = True
            self.refresh_models()

    def on_input_changed(self, event):
        if event.input.id == "model-search":
            self.render_models()

    def on_checkbox_changed(self, event):
        self.render_models()

    def render_models(self):
        search = self.query_one("#model-search", Input).value.casefold()
        free = self.query_one("#free-only", Checkbox).value
        matches = [
            m for m in self.models if (not free or m.free) and search in (m.id + " " + m.name).casefold()
        ]
        # Free router first; models that cannot output text (cannot write code) last.
        self.filtered_models = sorted(
            matches,
            key=lambda m: (
                m.id != "openrouter/free",
                m.id not in self.selected,
                m.text_output is False,
                m.name.casefold(),
            ),
        )
        listing = self.query_one("#model-list", OptionList)
        listing.clear_options()
        for m in self.filtered_models:
            cost = (
                "free"
                if m.free
                else f"${m.input_per_million}/{m.output_per_million} per million input/output tokens"
                if m.input_per_million is not None
                else "price unknown — set a request bound"
            )
            if m.id == "openrouter/free":
                label = "★ Free models router\n  picks an available free model for each request"
            elif m.id in self.selected:
                label = f"☆ {m.name}  (your shortlist)\n  {m.id} · {cost}"
            elif m.text_output is False:
                label = f"{m.name}  (cannot write code)\n  {m.id} · {cost}"
            else:
                label = f"{m.name}\n  {m.id} · {cost} · context {m.context or 'unknown'}"
            listing.add_option(Option(label, id=m.id, disabled=m.text_output is False))

    @work(thread=True, exclusive=True)
    def refresh_models(self):
        try:
            models, error = fetch(self.provider), None
        except Exception as exc:
            models, error = None, str(exc)
        self.app.call_from_thread(self.finish_refresh, models, error)

    def finish_refresh(self, models, error):
        if not self.is_mounted:
            return
        if models is not None:
            self.models = models
            self.query_one("#catalog-status", Static).update(f"{len(models)} models loaded")
            self.render_models()
        else:
            self.query_one("#catalog-status", Static).update(error)
        self.query_one("#refresh-models", Button).disabled = False

    def on_button_pressed(self, event):
        if event.button.id == "cancel-models":
            self.dismiss(None)
        elif event.button.id == "refresh-models":
            event.button.disabled = True
            self.refresh_models()

    def on_option_list_option_selected(self, event):
        model = next(m for m in self.filtered_models if m.id == event.option.id)
        self.dismiss(model)
