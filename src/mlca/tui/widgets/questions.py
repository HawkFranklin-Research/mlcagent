"""Docked questions with explicit sensitive decisions and a final review tab."""

from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Button, Input, Select, Static


class Questions(Vertical):
    DEFAULT_CSS = "Questions {height: auto; max-height: 23; border: round $accent; padding: 1;}"

    class Answer(Message):
        def __init__(self, qid, index=None, default=False, free_text=None):
            super().__init__()
            self.arguments = (qid, index, default, free_text)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.items, self.tab, self.selected = [], 0, 0

    def compose(self):
        yield Static("", id="question-tabs", markup=False)
        yield Static("", id="question-text", markup=False)
        yield Select([("Answer", 0)], allow_blank=False, id="question-answer")
        yield Input(placeholder="Type your own answer", id="question-custom")
        yield Button("Answer", id="question-submit")

    def show_questions(self, items):
        self.items = items
        self.display = bool(items)
        if not items:
            return
        self.tab = min(self.tab, len(items))
        self.query_one("#question-tabs", Static).update(
            " · ".join(
                [f"{'● ' if i == self.tab else ''}{q['header']}" for i, q in enumerate(items)] + ["Review"]
            )
        )
        review = self.tab == len(items)
        for widget in (Select, Input, Button):
            self.query_one(widget).display = not review
        if review:
            self.query_one("#question-text", Static).update(
                "Pending: " + "; ".join(q["question"] for q in items)
            )
            return
        q = items[self.tab]
        self.query_one("#question-text", Static).update(q["question"] + "\n" + q.get("why", ""))
        self.query_one(Select).set_options(
            [
                (o["label"] + (" (Recommended)" if i == q["recommended"] else ""), i)
                for i, o in enumerate(q["options"])
            ]
        )
        self.query_one(Select).value = q["recommended"]
        self.query_one(Input).value = ""

    def submit(self, default=False):
        if not self.items or self.tab == len(self.items):
            return
        q = self.items[self.tab]
        if default and q.get("explicit"):
            self.app.notify("Choose an explicit answer for this decision.", severity="warning")
            return
        self.post_message(
            self.Answer(
                q["question_id"], self.query_one(Select).value, default, self.query_one(Input).value or None
            )
        )

    def on_button_pressed(self, event):
        if event.button.id == "question-submit":
            event.stop()
            self.submit()

    def on_key(self, event):
        if event.key in {"left", "right"}:
            self.tab = (self.tab + (1 if event.key == "right" else -1)) % (len(self.items) + 1)
            self.show_questions(self.items)
        elif event.key == "escape":
            self.submit(True)
        elif event.key == "enter" and not isinstance(self.app.focused, Select):
            self.submit()
        else:
            return
        event.stop()
