from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, Input, Static

from mlca.llm.openai_auth import OpenAIFlow, save_profile


class OpenAISignin(ModalScreen[str | None]):
    CSS = """OpenAISignin { align: center middle; }
    #chatgpt-signin { width: 90%; max-width: 100; height: auto; max-height: 90%; border: round $accent; padding: 1 2; overflow-y: auto; }
    #chatgpt-signin Horizontal { height: 3; }"""

    def __init__(self, client_id):
        super().__init__()
        self.client_id = client_id
        self.flow = None
        self.busy = False
        self.finished = False

    def compose(self) -> ComposeResult:
        with Vertical(id="chatgpt-signin"):
            yield Static("Continue with ChatGPT")
            yield Static(
                "Use MLCA’s own registration. OpenAI asks you to approve plan usage and its limits; this does not grant access to ChatGPT conversations."
            )
            yield Checkbox("I approve MLCA requesting my ChatGPT plan allowance", id="chatgpt-consent")
            yield Static("", id="chatgpt-message", markup=False)
            yield Input(
                placeholder="SSH: paste the complete redirected URL", password=True, id="chatgpt-redirect"
            )
            with Horizontal():
                yield Button("Open browser", id="chatgpt-browser")
                yield Button("SSH / paste redirect", id="chatgpt-headless")
            with Horizontal():
                yield Button("Submit redirect", id="chatgpt-submit", disabled=True)
                yield Button("Cancel", id="chatgpt-cancel")

    def on_button_pressed(self, event):
        identifier = event.button.id
        if identifier == "chatgpt-cancel":
            self.finished = True
            if self.flow:
                self.flow.close()
            self.dismiss(None)
        elif identifier in {"chatgpt-browser", "chatgpt-headless"} and not self.busy:
            if not self.query_one("#chatgpt-consent", Checkbox).value:
                self.query_one("#chatgpt-message", Static).update(
                    "Approve requesting plan usage before continuing."
                )
                return
            try:
                if self.flow:
                    self.flow.close()
                self.flow = OpenAIFlow(self.client_id)
                self.query_one("#chatgpt-message", Static).update(self.flow.url)
                self.query_one("#chatgpt-submit", Button).disabled = identifier != "chatgpt-headless"
                if identifier == "chatgpt-browser":
                    self.flow.open_browser()
                    self.busy = True
                    self.finish_signin(wait=True)
            except Exception:
                self.query_one("#chatgpt-message", Static).update(
                    "Cannot start sign-in. Check MLCA registration and unlock your OS keyring."
                )
        elif identifier == "chatgpt-submit" and not self.busy:
            try:
                self.flow.accept(self.query_one("#chatgpt-redirect", Input).value)
                self.query_one("#chatgpt-redirect", Input).value = ""
                self.busy = True
                self.finish_signin()
            except Exception:
                self.query_one("#chatgpt-message", Static).update(
                    "Invalid, declined or expired redirect; start again."
                )

    @work(thread=True, exclusive=True)
    def finish_signin(self, wait=False):
        if self.finished:
            return
        try:
            if wait:
                self.flow.wait()
            profile = self.flow.exchange()
            if not self.finished:
                reference = save_profile(profile)
                self.app.call_from_thread(self.dismiss, reference)
        except Exception:
            if not self.finished:
                self.app.call_from_thread(
                    self.query_one("#chatgpt-message", Static).update,
                    "Sign-in failed. Check plan consent, registration, identity and secure storage; start again.",
                )
        finally:
            self.busy = False
            if self.flow:
                self.flow.close()

    def on_unmount(self):
        self.finished = True
        if self.flow:
            self.flow.close()
