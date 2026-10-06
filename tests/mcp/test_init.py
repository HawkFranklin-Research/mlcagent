import asyncio
import json

import pandas as pd
from mcp import Client
from mcp.types import Implementation

from mlca.api import Session
from mlca.mcp.server import create_server
from tests.mcp.helpers import data


def test_init_resolves_columns_without_interaction_and_scrubs_key(tmp_path, monkeypatch):
    source = tmp_path / "source.csv"
    pd.DataFrame({"x": range(20), "Outcome": [0, 1] * 10}).to_csv(source, index=False)
    root = tmp_path / "study"
    canary = "MLCA_INIT_FAKE_KEY_CANARY_14c92e"
    monkeypatch.setenv("MLCA_TEST_API_KEY", canary)
    monkeypatch.setattr(
        "mlca.llm.client.Client.complete",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("Model called")),
    )
    server = create_server(mode="brain")

    async def check():
        async with Client(server, client_info=Implementation(name="init-test", version="1")) as client:
            arguments = dict(
                path=str(root),
                data=[str(source)],
                template="tabular_classification",
                brief={"target": "Predict Outcome", "aim": canary},
            )
            result = data(await client.call_tool("mlca_init", arguments))
            assert result["initialized"] is False and result["columns_data"] == ["x", "Outcome"]
            assert not root.exists() and canary not in json.dumps(result)
            arguments["brief"]["target"] = "outcome"
            result = data(await client.call_tool("mlca_init", arguments))
            assert result["mode"] == "brain"
            session = server.controller.session
            assert session.state.columns["target"] == "Outcome"
            assert session.state.brief["target"] == "outcome"
            assert session.state.brief["aim"] == "[REDACTED]"
            head = session.state.head
            data(
                await client.call_tool(
                    "mlca_branch", {"action": "create", "name": "alternative", "from_id": head}
                )
            )
            checkout = data(
                await client.call_tool("mlca_branch", {"action": "checkout", "name": "alternative"})
            )
            assert set(checkout) == {"template", "event", "branch", "mode"}
            assert data(await client.call_tool("mlca_status", {}))["branch"] == "alternative"
            data(await client.call_tool("mlca_branch", {"action": "checkout", "name": "main"}))

    asyncio.run(check())
    assert canary not in (root / ".mlca/log/events.jsonl").read_text()
    with Session.open(root) as session:
        assert session.store.verify()["ok"]
        assert all(
            record.actor == "agent:init-test/1"
            for record in session.store.read()
            if record.type.value in {"BriefRecorded", "BranchCreated", "BranchCheckedOut"}
        )
