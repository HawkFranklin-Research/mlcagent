import asyncio

import pytest
from mcp import Client
from mcp.types import Implementation

from mlca.api import Session
from mlca.llm.usage import read
from mlca.mcp.server import create_server
from tests.helpers import choose_action
from tests.mcp.helpers import choose, data
from tests.mcp.test_brain import script


@pytest.mark.parametrize("mode", ["brain", "driver"])
def test_phases_journey_and_single_egress_envelope(project_factory, mode):
    root = project_factory()
    with Session.open(root, mode="brain") as human:
        choose_action(human, "confirm_brief")
        human.confirm("brief_confirmed", "Reviewed")
        human.next()
    server = create_server(root, mode)

    notifications = []

    async def received(progress, total, message):
        notifications.append(message)

    async def check():
        async with Client(server, client_info=Implementation(name="phases", version="1")) as client:
            before = len(read(root))
            status = data(await client.call_tool("mlca_status", {}))
            assert len(read(root)) == before + 1
            assert status["journey"]["events"][0]["state"] == "done"
            assert status["journey"]["events"][1]["state"] == "current"
            assert len(status["messages_data"]) <= 10
            outcome = await choose(client, "audit_schema")
            step_id = outcome["step_id"]
            if mode == "brain":
                assert outcome["phase"] == "awaiting_script"
                data(
                    await client.call_tool(
                        "mlca_submit_script",
                        {"step_id": step_id, "code": script("audit_schema")},
                        progress_callback=received,
                    )
                )
                for _ in range(300):
                    outcome = data(
                        await client.call_tool(
                            "mlca_step_status", {"step_id": step_id}, progress_callback=received
                        )
                    )
                    if outcome["status"] in {"completed", "failed"}:
                        break
                    await asyncio.sleep(0.03)
                assert any("checking" in str(n).lower() for n in notifications)
            assert outcome["status"] == "completed"
            status = data(await client.call_tool("mlca_status", {}))
            assert any(
                a.get("step_id") == step_id and a["actor"] == "agent:phases/1"
                for a in status["journey"]["actions"]
            )
            assert any("Step completed" in line for line in status["messages_data"])
            phases = [
                r.payload["phase"]
                for r in server.controller.session.store.read()
                if r.type.value == "StepProgress" and r.step_id == step_id
            ]
            expected = (["awaiting_script"] if mode == "brain" else ["writing"]) + [
                "checking",
                "running",
                "collecting",
                "checking_subgoals",
                "completed",
            ]
            assert phases == expected
            assert outcome["phase"] == "completed"

    asyncio.run(check())
