"""Capture a synthetic, offline first-run UI. No provider or original data calls."""

import asyncio
import os
import tempfile
from pathlib import Path

import yaml

from mlca.config import Config, ProviderConfig, RoleConfig
from mlca.project.init import initialise
from mlca.tui.app import MlcaApp
from mlca.tui.screens.onboarding import OnboardingScreen


async def capture(root, output):
    app = MlcaApp(root.parent / "welcome")
    async with app.run_test(size=(120, 45)) as pilot:
        await pilot.pause()
        app.save_screenshot(str(output / "welcome.svg"))
        app.open_project(root)
        await pilot.pause()
        await app.workers.wait_for_complete()
        await pilot.pause()
        app.save_screenshot(str(output / "guided-study.svg"))
        app.push_screen(OnboardingScreen(Config()))
        await pilot.pause()
        app.save_screenshot(str(output / "models.svg"))
        app.screen.dismiss(None)
        app.action_quit()


def main():
    output = Path(__file__).resolve().parents[1] / "docs/screens"
    output.mkdir(exist_ok=True)
    cache = Path.home() / ".cache/mlca-ui-capture"
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        base = Path(directory)
        os.environ["XDG_CONFIG_HOME"] = str(base / "config")
        os.environ["XDG_DATA_HOME"] = str(base / "userdata")
        os.environ["UV_OFFLINE"] = "1"
        data = base / "synthetic.csv"
        data.write_text("x,y\n1,0\n2,1\n3,0\n4,1\n")
        fake = base / "fake.yaml"
        fake.write_text(
            yaml.safe_dump(
                {
                    "responses": [
                        {
                            "match": {"role": "navigator", "purpose": "options"},
                            "response": {
                                "options": [
                                    {
                                        "id": "1",
                                        "action_id": "confirm_brief",
                                        "params": {},
                                        "title": "Record brief and data inventory",
                                        "why_now": "Fix the question before analyzing data",
                                        "advances": ["outputs_recorded"],
                                        "expected_outputs": ["brief.json"],
                                    }
                                ]
                            },
                        }
                    ]
                }
            )
        )
        role = RoleConfig(provider="offline", model="scripted")
        config = Config(
            providers={"offline": ProviderConfig(kind="fake", script=str(fake))},
            roles={"navigator": role, "worker": role},
        )
        root = initialise(
            base / "study",
            [data],
            "tabular_classification",
            {"aim": "Predict the outcome", "target": "", "unit": ""},
            config.model_dump(),
        )
        asyncio.run(capture(root, output))


if __name__ == "__main__":
    main()
