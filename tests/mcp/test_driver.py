import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from mcp import Client
from mcp.types import Implementation
from typer.testing import CliRunner

from mlca.api import Session
from mlca.cli.main import app
from mlca.errors import MlcaUserError
from mlca.mcp.server import create_server
from tests.mcp.helpers import choose, data, poll


@pytest.mark.slow
def test_driver_full_path(project_factory):
    root = project_factory()
    server = create_server(root, "driver")

    async def check():
        async with Client(server, client_info=Implementation(name="driver-test", version="1")) as client:
            for event in [
                "onboard",
                "data",
                "eda",
                "split",
                "preprocess",
                "features",
                "model",
                "validate",
                "test",
                "interpret",
                "report",
            ]:
                s = server.controller.require("agent:driver-test/1")
                assert s.state.current_event == event
                if event == "test":
                    request = data(
                        await client.call_tool(
                            "mlca_request_approval",
                            dict(kind="unlock_test", target="test", reason="planned test"),
                        )
                    )
                    result = CliRunner().invoke(
                        app,
                        [
                            "--project",
                            str(root),
                            "approvals",
                            "approve",
                            request["request_id"],
                            "--phrase",
                            "UNLOCK TEST",
                        ],
                    )
                    assert result.exit_code == 0, result.output
                action = s.workflow.events[event].default_options[0]
                outcome = await choose(client, action)
                assert outcome["status"] == "completed", outcome
                if event in {"onboard", "validate"}:
                    target = "brief_confirmed" if event == "onboard" else "model_selected"
                    request = data(
                        await client.call_tool(
                            "mlca_request_approval",
                            dict(kind="confirm", target=target, reason="review evidence"),
                        )
                    )
                    result = CliRunner().invoke(
                        app,
                        [
                            "--project",
                            str(root),
                            "approvals",
                            "approve",
                            request["request_id"],
                            "--note",
                            "reviewed",
                        ],
                    )
                    assert result.exit_code == 0, result.output
                moved = data(await client.call_tool("mlca_move", {"to": "next"}))
                assert moved.get("entered") or moved.get("complete"), moved
            result = data(await client.call_tool("mlca_report", {"kind": "usage"}))
            assert result["paths_data"]
            assert s.store.verify()["ok"]
            assert any(
                r.actor == "agent:driver-test/1" and r.type.value == "OptionChosen" for r in s.store.read()
            )

    asyncio.run(check())


@pytest.mark.slow
def test_background_lock_both_directions(project_factory, monkeypatch):
    from mlca.roles.worker import Worker

    root = project_factory()
    with Session.open(root) as s:
        s.choose("1")
        s.confirm("brief_confirmed", "reviewed")
        s.next()
    entered, release = threading.Event(), threading.Event()
    original = Worker.write_script

    def blocked(self, *args):
        entered.set()
        assert release.wait(20)
        return original(self, *args)

    monkeypatch.setattr(Worker, "write_script", blocked)

    async def check():
        server = create_server(root, "driver")
        async with Client(server) as client:
            menu = data(await client.call_tool("mlca_options", {}))
            before = time.monotonic()
            result = data(await client.call_tool("mlca_choose", {"option_id": menu["options"][0]["id"]}))
            assert time.monotonic() - before < 2
            assert await asyncio.to_thread(entered.wait, 2)
            try:
                with Session.open(root) as human:
                    with pytest.raises(MlcaUserError, match="Project busy"):
                        human.choose("1")
            finally:
                release.set()
            assert (await poll(client, result["step_id"]))["status"] == "completed"

    asyncio.run(check())
    # CLI/API owns the lock first; a second MCP mutation must refuse promptly.
    with Session.open(root) as s:
        s.next()
        entered.clear()
        release.clear()
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(s.choose, "1")
            assert entered.wait(10)

            async def other():
                server = create_server(root, "driver")
                async with Client(server) as client:
                    result = await client.call_tool("mlca_custom", {"text": "Describe distributions"})
                    assert result.is_error and "Project busy" in result.content[0].text

            try:
                asyncio.run(other())
            finally:
                release.set()
            assert future.result()["status"] == "completed"
