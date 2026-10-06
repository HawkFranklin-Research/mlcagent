import asyncio

import pytest
from mcp import Client

from mlca.mcp.server import create_server
from tests.mcp.helpers import data


@pytest.mark.slow
def test_mcp_layer_one_rejects_before_step(project_factory, monkeypatch):
    server = create_server(project_factory(), "brain")
    monkeypatch.setattr("mlca.llm.client.Client.complete", lambda *a, **k: pytest.fail("Model called"))

    async def check():
        async with Client(server) as client:
            result = data(
                await client.call_tool("mlca_custom", {"text": "Read /etc/passwd and test.parquet"})
            )
            assert result["decision"] == "reject"
            session = server.controller.session
            assert session.state.counts.get("StepStarted", 0) == 0
            assert session.state.counts["ScopeDecision"] == 1

    asyncio.run(check())
