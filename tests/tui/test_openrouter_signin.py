import asyncio

from textual.widgets import Input

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
            for _ in range(20):
                await pilot.pause()
                if results:
                    break
            # Sign-in saves at once: no separate Save step.
            assert results, "sign-in did not save the configuration"
            assert app.screen is not screen

    try:
        asyncio.run(check())
        assert "tui-signin-canary" not in str(results)
        assert results[0]["config"]["roles"]["worker"]["model"] == "openrouter/free"
    finally:
        credentials.forget()
