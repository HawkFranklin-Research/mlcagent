import time

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import LoadingIndicator, Static


class Progress(Vertical):
    DEFAULT_CSS = """Progress { height: auto; border: round $accent; padding: 0 1; }
    Progress Horizontal { height: 2; } Progress LoadingIndicator { width: 5; }
    Progress Static { width: 1fr; height: auto; }"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clock = time.monotonic
        self.started_at = None
        self.label = "Ready"
        self.phases = []

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield LoadingIndicator(id="agent-spinner")
            yield Static("Ready", id="agent-progress", markup=False)

    def on_mount(self):
        self.query_one(LoadingIndicator).display = False
        self.set_interval(0.25, self.tick)

    def start(self, operation, model):
        self.started_at = self.clock()
        self.label = (
            ("Agent is preparing options…" if operation == "options" else "Preparing your step…")
            + " · "
            + model
        )
        self.phases = []
        self.query_one(LoadingIndicator).display = True
        self.tick()

    def phase(self, payload):
        phase = payload["phase"]
        if phase not in self.phases:
            self.phases.append(phase)
        attempt = (
            f" · attempt {payload['attempt']}/{payload.get('max_attempts', 3)}"
            if payload.get("attempt")
            else ""
        )
        self.label = phase + attempt
        if payload.get("reason"):
            self.label += " · " + payload["reason"][:180]
        self.tick()

    def tick(self):
        elapsed = f" · {self.clock() - self.started_at:.1f}s" if self.started_at is not None else ""
        self.query_one("#agent-progress", Static).update(self.label + elapsed)

    def finish(self, error=None, note=None):
        if error:
            self.label = "Action failed: " + error[:180]
        elif note:
            self.label = note
        else:
            self.label = "Ready — choose your next card"
        self.started_at = None
        self.query_one(LoadingIndicator).display = False
        self.tick()
