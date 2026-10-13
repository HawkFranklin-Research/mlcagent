import asyncio

from textual.app import App
from textual.widgets import Checkbox, Select

from mlca.config import Config, ProviderConfig, RoleConfig
from mlca.tui.screens.onboarding import OnboardingScreen


def test_advanced_privacy_settings_are_saved():
    config = Config(
        providers={"test": ProviderConfig(kind="fake", script="unused.yaml")},
        roles={role: RoleConfig(provider="test", model="scripted") for role in ("navigator", "worker")},
    )
    results = []

    async def check():
        app = App()
        async with app.run_test(size=(130, 60)) as pilot:
            screen = OnboardingScreen(config)
            app.push_screen(screen, results.append)
            await pilot.pause()
            screen.query_one("#provider-data-collection", Select).value = "deny"
            screen.query_one("#provider-zdr", Checkbox).value = True
            screen.save_settings()
            await pilot.pause()

    asyncio.run(check())
    assert results[0]["config"]["privacy"]["provider_data_collection"] == "deny"
    assert results[0]["config"]["privacy"]["zero_data_retention"] is True
