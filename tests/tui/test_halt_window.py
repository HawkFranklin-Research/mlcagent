import asyncio

from textual.widgets import Static

from mlca.tui.app import MlcaApp
from mlca.tui.widgets.progress import Progress


def test_tui_countdown_and_halt_with_no_model_call(project_factory, monkeypatch):
    root = project_factory()

    def decision(session):
        session.decision_window.decide(session, "choice", 0, [{"title": "Fit baseline"}])

    monkeypatch.setattr("mlca.autonomous.runner.drive", decision)

    async def check():
        app = MlcaApp(root)
        async with app.run_test(size=(120, 45)) as pilot:
            await pilot.pause()
            await app.workers.wait_for_complete()
            app.action_autopilot()
            for _ in range(30):
                await pilot.pause(0.05)
                if any(r.type.value == "DecisionWindowOpened" for r in app.session.store.read()):
                    break
            assert app.busy
            await pilot.pause(0.15)
            label = str(app.screen.query_one(Progress).query_one("#agent-progress", Static).content)
            assert "Fit baseline" in label and "Halt" in label
            await pilot.press("h")
            await app.workers.wait_for_complete()
            assert not app.busy
            records = app.session.store.read()
            assert any(r.type.value == "DecisionWindowHalted" and r.actor == "user" for r in records)
            assert not any(r.type.value == "OptionChosen" for r in records)
            assert app.session.principal == "user"
            app.action_quit()

    asyncio.run(check())
