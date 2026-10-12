import asyncio

from textual.widgets import Button

from mlca.config import Config
from mlca.tui.app import MlcaApp
from mlca.tui.screens.onboarding import OnboardingScreen


def test_chatgpt_button_disabled_before_registration(tmp_path):
    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(100, 35)) as pilot:
            app.push_screen(OnboardingScreen(Config()))
            await pilot.pause()
            assert app.screen.query_one("#chatgpt-signin", Button).disabled
            assert "coming soon" in str(app.screen.query_one("#chatgpt-signin", Button).label)

    asyncio.run(check())
