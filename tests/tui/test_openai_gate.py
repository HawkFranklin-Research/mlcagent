import asyncio

from textual.widgets import Button

from mlca.config import Config
from mlca.tui.app import MlcaApp
from mlca.tui.screens.onboarding import OnboardingScreen


def test_chatgpt_sign_in_available_before_registration(tmp_path):
    # The first sign-in registers MLCA; only sign-out waits for an issued client ID.
    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(100, 35)) as pilot:
            app.push_screen(OnboardingScreen(Config()))
            await pilot.pause()
            assert not app.screen.query_one("#chatgpt-signin", Button).disabled
            assert app.screen.query_one("#chatgpt-signout", Button).disabled

    asyncio.run(check())
