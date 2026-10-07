import asyncio

import pytest
from mcp import Client

from mlca.api import Session
from mlca.mcp.server import create_server
from tests.helpers import advance_to
from tests.mcp.helpers import choose, data, poll
from tests.mcp.test_brain import submit

COUNT = """import pandas as pd, mlca_runtime as m
df = pd.read_csv(list(m.inputs().values())[0])
counts = df.y.value_counts().rename_axis("class").reset_index(name="n")
counts["share"] = counts.n / len(df)
m.save_table(counts, "target_counts.csv")
"""
AUDIT = """import pandas as pd, mlca_runtime as m
df = pd.read_csv(list(m.inputs().values())[0])
m.save_table(pd.DataFrame({"column": df.columns, "dtype": df.dtypes.astype(str).values}), "schema.json")
"""


@pytest.mark.parametrize("before", [True, False])
def test_supporting_and_custom_preserve_completion(project_factory, monkeypatch, before):
    root = project_factory()
    with Session.open(root) as human:
        advance_to(human, "data")
    monkeypatch.setattr("mlca.llm.client.Client.complete", lambda *a, **kw: pytest.fail("Model called"))
    server = create_server(root, "brain")

    async def run(client, action, source):
        pending = await choose(client, action)
        assert (await submit(client, pending["step_id"], source))["status"] == "completed"

    async def check():
        async with Client(server) as client:
            menu = data(await client.call_tool("mlca_options", {}))["options"]
            assert [o.get("action_id") for o in menu[:2]] == ["audit_schema", "count_target"]
            if before:
                await run(client, "count_target", COUNT)
                assert server.controller.session.state.event_statuses["data"] == "open"
            await run(client, "audit_schema", AUDIT)
            session = server.controller.session
            assert session.state.event_statuses["data"] == "done"
            generation = session.state.generations["data"]
            menu = data(await client.call_tool("mlca_options", {}))["options"]
            assert menu[0]["id"].endswith(":next") and menu[-1]["id"].endswith(":custom")
            assert any(o.get("action_id") == "count_target" for o in menu) is (not before)
            primary = {
                "id": "1",
                "action_id": "audit_schema",
                "title": "Again",
                "why_now": "retry",
                "params": {},
                "advances": [],
                "expected_outputs": ["schema.json"],
            }
            refused = await client.call_tool("mlca_submit_options", {"options": [primary]})
            assert refused.is_error and "supporting actions only" in refused.content[0].text
            if not before:
                option = next(o for o in menu if o.get("action_id") == "count_target")
                proposal = {k: option[k] for k in primary}
                data(await client.call_tool("mlca_submit_options", {"options": [proposal]}))
                await run(client, "count_target", COUNT)
            menu = data(await client.call_tool("mlca_options", {}))["options"]
            assert not any(o.get("action_id") for o in menu)
            rejected = data(
                await client.call_tool("mlca_custom", {"text": "Train a model and read test set"})
            )
            assert rejected["decision"] == "reject"
            pending = data(await client.call_tool("mlca_custom", {"text": "Summarize column types"}))
            if pending["status"] != "awaiting_script":
                pending = await poll(client, pending["step_id"])
            source = 'import pandas as pd, mlca_runtime as m\nm.save_table(pd.DataFrame({"summary": ["types reviewed"]}), "inspection.csv")\n'
            assert (await submit(client, pending["step_id"], source))["status"] == "completed"
            assert session.state.event_statuses["data"] == "done"
            assert session.state.generations["data"] == generation
            assert all(
                session.state.subgoals["data." + g.id]["passed"]
                for g in session.workflow.events["data"].subgoals
            )
            data(await client.call_tool("mlca_move", {"to": "next"}))
            assert session.state.current_event == "eda"

    asyncio.run(check())
