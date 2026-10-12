import asyncio

from textual.widgets import Input, Select

from mlca.tui.app import MlcaApp
from mlca.tui.screens.main import MainScreen
from mlca.tui.screens.study import StudyScreen
from mlca.tui.widgets.options import OptionCard, Options


def test_new_user_reaches_data_using_cards_only(project_factory):
    root = project_factory(brief={"aim": "Predict the outcome", "target": "", "unit": ""})

    async def check():
        app = MlcaApp(root)
        async with app.run_test(size=(120, 45)) as pilot:

            async def settle():
                await pilot.pause()
                await app.workers.wait_for_complete()
                await pilot.pause()

            async def click(identifier):
                card = next(c for c in app.screen.query(OptionCard) if c.option_id == identifier)
                card.scroll_visible(animate=False)
                await pilot.pause()
                await pilot.click("#" + card.id)
                await settle()

            await settle()
            assert isinstance(app.screen, MainScreen)
            await click("human:study")
            assert isinstance(app.screen, StudyScreen)
            app.screen.query_one("#study-target", Select).value = "y"
            app.screen.query_one("#study-unit", Input).value = "One sample"
            app.screen.query_one("#study-save").scroll_visible(animate=False)
            await pilot.pause()
            await pilot.click("#study-save")
            await settle()
            assert app.session.state.columns["target"] == "y"
            # Record the brief, then explicitly confirm it, all through visible cards.
            ordinary = next(
                o["id"] for o in app.screen.query_one(Options).items if o.get("action_id") == "confirm_brief"
            )
            await click(ordinary)
            await click("human:confirm:brief_confirmed")
            app.screen.query_one("#note", Input).value = "Reviewed my question and target"
            await pilot.click("#submit")
            await settle()
            await click("next")
            assert app.session.state.current_event == "data"
            assert app.screen.query_one(Options).items[-1]["id"] == "custom"
            assert "exhausted" not in str(app.screen.query_one(Options).items).lower()
            app.action_quit()

    asyncio.run(check())
