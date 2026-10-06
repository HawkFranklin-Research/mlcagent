import asyncio

import pytest
from rich.console import Console
from textual.widgets import Footer, Static

from mlca.tui.app import MlcaApp
from mlca.tui.screens.main import MainScreen
from mlca.tui.screens.welcome import WelcomeScreen
from mlca.tui.widgets.log_stream import record_summary, result_summary


def test_welcome_banner_footer_and_quit(tmp_path):
    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, WelcomeScreen)
            console = Console(width=120)
            with console.capture() as capture:
                console.print(app.screen.query_one("#banner", Static).content)
            assert "Machine Learning Copilot Agent" in capture.get()
            app.screen.query_one(Footer)
            assert {key for key, active in app.screen.active_bindings.items() if active.binding.show} == {
                "o",
                "i",
                "s",
                "q",
            }
            await pilot.press("q")

    asyncio.run(check())


@pytest.mark.slow
def test_main_opens_project_and_quits(project_factory):
    root = project_factory()

    async def check():
        app = MlcaApp(root)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            await app.workers.wait_for_complete()
            assert isinstance(app.screen, MainScreen)
            assert app.session.state.columns == {"target": "y"}
            await pilot.press("q")

    asyncio.run(check())


def test_readable_log():
    from types import SimpleNamespace

    options = [{"id": "1", "title": "Audit schema"}, {"id": "custom", "title": "Custom"}]
    assert result_summary("options", options) == "options: 1 Audit schema · custom"
    record = SimpleNamespace(
        type=SimpleNamespace(value="SubgoalChecked"), payload={"subgoal_id": "schema", "passed": True}
    )
    assert record_summary(record) == "SubgoalChecked: schema · passed"
