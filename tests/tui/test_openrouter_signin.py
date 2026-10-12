import asyncio

from textual.widgets import Button, Input, Static

from mlca.config import Config
from mlca.llm import credentials
from mlca.tui.app import MlcaApp
from mlca.tui.screens.onboarding import OnboardingScreen
from mlca.tui.screens.openrouter_signin import OpenRouterSignin


def test_headless_signin_sets_free_router_without_key_in_config(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "mlca.tui.screens.openrouter_signin.secure_backend", lambda: (_ for _ in ()).throw(ValueError())
    )
    monkeypatch.setattr("mlca.llm.openrouter_auth.Flow.exchange", lambda self: "tui-signin-canary")
    credentials.forget()
    results = []

    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(120, 45)) as pilot:
            screen = OnboardingScreen(Config())
            app.push_screen(screen, results.append)
            await pilot.pause()
            await pilot.click("#start-free")
            await pilot.pause()
            assert isinstance(app.screen, OpenRouterSignin)
            await pilot.click("#signin-headless")
            app.screen.query_one("#signin-code", Input).value = "one-use-code"
            await pilot.click("#signin-submit")
            for _ in range(10):
                await pilot.pause()
                if app.screen is screen:
                    break
            assert app.screen is screen
            assert screen.query_one("#navigator-model", Input).value == "openrouter/free"
            assert screen.query_one("#navigator-key", Input).value == ""
            button = screen.query_one("#save-settings", Button)
            button.scroll_visible(animate=False)
            await pilot.pause()
            await pilot.click("#save-settings")
            await pilot.pause()
            assert results, screen.query_one("#settings-error", Static).content

    try:
        asyncio.run(check())
        assert "tui-signin-canary" not in str(results)
        assert results[0]["config"]["roles"]["worker"]["model"] == "openrouter/free"
    finally:
        credentials.forget()
