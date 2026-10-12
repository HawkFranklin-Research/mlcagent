from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Static

from mlca.llm.openrouter_auth import Flow, secure_backend, store_key


class OpenRouterSignin(ModalScreen[str | None]):
    CSS = """OpenRouterSignin { align: center middle; }
    #router-signin { width: 90%; max-width: 110; height: auto; max-height: 95%;
        padding: 1 2; border: round $accent; overflow-y: auto; }
    .signin-buttons { height: 3; } #signin-code { margin: 1 0; }"""

    def __init__(self):
        super().__init__()
        self.flow = None
        self.busy = False
        self.finished = False

    def compose(self) -> ComposeResult:
        with Vertical(id="router-signin"):
            yield Static("Start free with OpenRouter")
            yield Static(
                "Sign into your own OpenRouter account. MLCA receives a user-owned key; no MLCA server is involved."
            )
            try:
                secure_backend()
                persistent = True
            except Exception:
                persistent = False
            yield Checkbox(
                "Remember in secure OS keyring",
                value=persistent,
                disabled=not persistent,
                id="signin-persist",
            )
            yield Static("If secure storage is unavailable, the key stays only in this application session.")
            yield Static(
                "Free inference has quotas (currently typically 50 requests/day without purchased credits). A study may exceed your quota. No paid fallback is configured."
            )
            yield Static("", id="signin-message")
            yield Input(placeholder="Headless authorization code", password=True, id="signin-code")
            with Horizontal(classes="signin-buttons"):
                yield Button("Open browser", id="signin-browser", variant="primary")
                yield Button("SSH / paste code", id="signin-headless")
            with Horizontal(classes="signin-buttons"):
                yield Button("Submit code", id="signin-submit", disabled=True)
                yield Button("Cancel", id="signin-cancel")

    def on_button_pressed(self, event):
        identifier = event.button.id
        if identifier == "signin-cancel":
            self.finished = True
            if self.flow:
                self.flow.close()
            self.dismiss(None)
        elif identifier in {"signin-browser", "signin-headless"} and not self.busy:
            if self.flow:
                self.flow.close()
            try:
                self.flow = Flow(headless=identifier == "signin-headless")
            except Exception:
                self.query_one("#signin-message", Static).update(
                    "Could not start the local callback; use SSH / paste code."
                )
                return
            self.query_one("#signin-message", Static).update(self.flow.url)
            self.query_one("#signin-submit", Button).disabled = identifier != "signin-headless"
            if identifier == "signin-browser":
                try:
                    self.flow.open_browser()
                except Exception:
                    self.query_one("#signin-message", Static).update(
                        "Open this URL manually: " + self.flow.url
                    )
                self.busy = True
                self.finish_signin(wait=True, persistent=self.query_one("#signin-persist", Checkbox).value)
        elif identifier == "signin-submit" and not self.busy:
            try:
                self.flow.accept(self.query_one("#signin-code", Input).value)
                self.query_one("#signin-code", Input).value = ""
                self.busy = True
                self.finish_signin(persistent=self.query_one("#signin-persist", Checkbox).value)
            except Exception:
                self.query_one("#signin-message", Static).update("Invalid or expired code; start again.")

    @work(thread=True, exclusive=True)
    def finish_signin(self, wait=False, persistent=False):
        if self.finished:
            return
        try:
            if wait:
                self.flow.wait()
            key = self.flow.exchange()
            if self.finished:
                return
            reference = store_key(key, persistent=persistent)
            if not self.finished:
                self.app.call_from_thread(self.dismiss, reference)
        except Exception:
            if not self.finished:
                self.app.call_from_thread(
                    self.query_one("#signin-message", Static).update,
                    "Sign-in failed, cancelled or expired. Check secure storage or use session-only and start again.",
                )
        finally:
            self.busy = False
            if self.flow:
                self.flow.close()

    def on_unmount(self):
        self.finished = True
        if self.flow:
            self.flow.close()
