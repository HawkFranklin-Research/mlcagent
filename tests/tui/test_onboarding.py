import asyncio

from textual.widgets import Checkbox, DirectoryTree, Input, Select, Static

from mlca.config import Config, ProviderConfig, RoleConfig
from mlca.tui.app import MlcaApp
from mlca.tui.screens.file_picker import FilePicker
from mlca.tui.screens.model_picker import ModelPicker
from mlca.tui.screens.onboarding import OnboardingScreen
from mlca.tui.screens.project import ProjectScreen


def test_dynamic_project_form_and_directory(tmp_path):
    data = tmp_path / "table.csv"
    data.write_text("age,outcome\n20,0\n30,1\n")

    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(100, 35)) as pilot:
            screen = ProjectScreen(tmp_path / "new", initialise=True)
            app.push_screen(screen)
            await pilot.pause()
            assert not screen.query_one("#event_column").display
            screen.find_tables()
            assert screen.files == []
            assert "Choose a data file" in str(screen.query_one("#form-error", Static).content)
            screen.query_one("#data", Input).value = str(tmp_path)
            screen.find_tables()
            await pilot.pause()
            assert screen.query_one("#primary", Select).value == "table"
            assert screen.columns == ["age", "outcome"]
            assert screen.query_one("#target", Select).value == ""
            screen.query_one("#template", Select).value = "survival"
            await pilot.pause()
            assert screen.query_one("#duration").display
            assert screen.query_one("#event_column").display
            assert not screen.query_one("#target").display
            screen.dismiss(None)
            app.push_screen(FilePicker(tmp_path))
            await pilot.pause()
            picker = app.screen
            tree = picker.query_one(DirectoryTree)
            tree.post_message(DirectoryTree.DirectorySelected(tree.root, tmp_path))
            await pilot.pause()
            assert picker.query_one("#picked-path", Input).value == str(tmp_path)
            app.screen.dismiss(None)
            await pilot.pause()

    asyncio.run(check())


def test_provider_screen_preserves_assignments(tmp_path):
    config = Config(
        providers={
            "first_unused": ProviderConfig(kind="openai_api", api_key_env="NOT_AVAILABLE"),
            "router": ProviderConfig(
                kind="openrouter", api_key_env="ROUTER_TEST", request_cost_bound_usd=0.1
            ),
            "local": ProviderConfig(
                kind="openai_compatible", base_url="http://localhost:1234/v1", request_cost_bound_usd=0.1
            ),
        },
        roles={
            "navigator": RoleConfig(provider="router", model="nav", temperature=0.2),
            "worker": RoleConfig(provider="local", model="coder", max_output_tokens=8192),
        },
    )
    results = []

    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(100, 35)) as pilot:
            screen = OnboardingScreen(config)
            app.push_screen(screen, results.append)
            await pilot.pause()
            assert screen.query_one("#navigator-kind", Select).value == "openrouter"
            assert screen.query_one("#worker-kind", Select).value == "openai_compatible"
            assert screen.query_one("#navigator-key", Input).password
            screen.query_one("#navigator-key", Input).value = "settings-canary-key"
            # The submit button can be scrolled into view even on a small terminal.
            button = screen.query_one("#save-settings")
            button.scroll_visible(animate=False)
            await pilot.pause()
            await pilot.click("#save-settings")
            await pilot.pause()
            assert results, screen.query_one("#settings-error", Static).content

    asyncio.run(check())
    updated = Config.model_validate(results[0]["config"])
    assert updated.roles["navigator"].provider == "router"
    assert updated.roles["worker"].provider == "local"
    assert updated.roles["worker"].max_output_tokens == 8192
    assert updated.roles["navigator"].temperature == 0.2
    assert "first_unused" in updated.providers
    assert "settings-canary-key" not in str(results)


def test_model_picker_offline_and_free_filter(tmp_path, monkeypatch):
    from mlca.llm.catalog import Model

    monkeypatch.setattr(
        "mlca.tui.screens.model_picker.cached",
        lambda _: ([Model("free", "Free", 0, 0, free=True), Model("paid", "Paid", 1, 2)], False),
    )

    async def check():
        app = MlcaApp(tmp_path)
        async with app.run_test(size=(80, 30)) as pilot:
            screen = ModelPicker(ProviderConfig(kind="openrouter"))
            app.push_screen(screen)
            await pilot.pause()
            assert len(screen.filtered_models) == 2
            screen.query_one("#free-only", Checkbox).value = True
            await pilot.pause()
            assert [m.id for m in screen.filtered_models] == ["free"]
            screen.query_one("#model-search", Input).value = "absent"
            await pilot.pause()
            assert screen.filtered_models == []

    asyncio.run(check())
