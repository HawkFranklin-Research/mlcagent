import asyncio

from textual.app import App
from textual.widgets import Static

from mlca.tui.widgets.progress import Progress


def test_progress_phases_and_fake_clock():
    class Harness(App):
        def compose(self):
            yield Progress()

    async def check():
        app = Harness()
        async with app.run_test():
            widget = app.query_one(Progress)
            now = [10.0]
            widget.clock = lambda: now[0]
            widget.start("options", "selected-model")
            now[0] = 12.0
            widget.tick()
            assert "preparing options" in str(widget.query_one(Static).content)
            assert "2.0s" in str(widget.query_one(Static).content)
            for phase in [
                "Writing the script",
                "Checking the script",
                "Running in the sandbox",
                "Collecting outputs",
                "Checking sub-goals",
            ]:
                widget.phase({"phase": phase, "attempt": 2, "max_attempts": 3})
            assert len(widget.phases) == 5
            widget.finish("Runtime error")
            assert "Runtime error" in str(widget.query_one(Static).content)

    asyncio.run(check())
