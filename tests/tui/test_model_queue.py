import asyncio
from types import SimpleNamespace as NS

from textual.widgets import Input

from mlca.config import Config, ProviderConfig, RoleConfig
from mlca.tui.app import MlcaApp
from mlca.tui.screens.onboarding import OnboardingScreen


def test_busy_model_switch_is_queued_until_step_end(tmp_path):
    role = RoleConfig(provider="offline", model="old")
    config = Config(
        providers={"offline": ProviderConfig(kind="fake", script="not-used")},
        roles={"navigator": role, "worker": role},
    )

    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(120, 45)) as pilot:
            app.session = NS(config=config, active_step=lambda: {"step_id": "running"})
            app.busy = True
            app.action_configure()
            await pilot.pause()
            assert isinstance(app.screen, OnboardingScreen)
            app.screen.query_one("#navigator-model", Input).value = "new"
            app.screen.query_one("#save-settings").scroll_visible(animate=False)
            await pilot.pause()
            await pilot.click("#save-settings")
            await pilot.pause()
            assert app.pending_config.roles["worker"].model == "new"
            assert app.session.config.roles["worker"].model == "old"
            app.busy = False
            app.session = None

    asyncio.run(check())
