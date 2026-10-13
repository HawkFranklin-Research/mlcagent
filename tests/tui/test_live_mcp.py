import asyncio
import threading
import time

from textual.widgets import Input

from mlca.api import Session
from mlca.tui.app import MlcaApp
from mlca.tui.widgets.options import OptionCard
from mlca.tui.widgets.status_bar import StatusBar
from tests.helpers import choose_action


def test_external_session_updates_tui_and_human_approval_while_waiting(project_factory, monkeypatch):
    root = project_factory()
    agent = Session.open(root, client="mcp", principal="agent:claude/1", mode="brain")
    choose_action(agent, "confirm_brief")
    request = agent.request_approval("confirm", "brief_confirmed", "Review the brief")
    waiting = agent.custom("Summarize the study brief")
    assert waiting["status"] == "awaiting_script"
    monkeypatch.setattr(
        "mlca.llm.client.Client.complete",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("No model calls")),
    )

    async def check():
        app = MlcaApp(root)
        async with app.run_test(size=(120, 45)) as pilot:
            await pilot.pause()
            await app.workers.wait_for_complete()
            assert "Brain mode" in str(app.screen.query_one(StatusBar).render())
            assert "not connected" not in str(app.screen.query_one(StatusBar).render())
            thread = threading.Thread(target=lambda: agent.emit("Note", {"text": "External activity"}))
            thread.start()
            thread.join()
            started = time.monotonic()
            while (
                not app._external_head or app._external_head[0] != agent.state.head
            ) and time.monotonic() - started < 1.9:
                await pilot.pause(0.1)
            assert time.monotonic() - started < 2
            assert app._external_head[0] == agent.state.head
            assert any(
                c.disabled for c in app.screen.query(OptionCard) if not c.option_id.startswith("human:")
            )
            app.action_approvals()
            await pilot.pause()
            app.screen.query_one("#id", Input).value = request["request_id"]
            app.screen.query_one("#decision", Input).value = "approve"
            app.screen.query_one("#note", Input).value = "Reviewed"
            app.screen.query_one("#submit").scroll_visible(animate=False)
            await pilot.pause()
            await pilot.click("#submit")
            await app.workers.wait_for_complete()
            await pilot.pause()
            assert app.session.approvals() == []
            assert app.session.state.confirmations
            assert app.session.active_step()["status"] == "awaiting_script"
            app.action_quit()

    try:
        asyncio.run(check())
    finally:
        agent.close()
