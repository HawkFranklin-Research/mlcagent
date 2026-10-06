import asyncio
import json
import sys

import pytest
from mcp import Client, StdioServerParameters
from mcp.types import Implementation

from mlca.mcp.server import create_server


def data(result):
    assert not result.is_error, result
    return json.loads(result.content[0].text)["data"]


def test_stdio_and_read_schemas():
    async def check():
        async with Client(
            StdioServerParameters(command=sys.executable, args=["-m", "mlca", "mcp"]), read_timeout_seconds=10
        ) as client:
            tools = await client.list_tools()
            assert len(tools.tools) == 12
            assert all("ctx" not in tool.input_schema["properties"] for tool in tools.tools)
            assert all(tool.annotations.destructive_hint is False for tool in tools.tools)
            assert client.protocol_version in {"2026-07-28", "2025-11-25", "2025-06-18"}

    asyncio.run(check())


@pytest.mark.slow
def test_read_modes_and_identity(project_factory):
    root = project_factory()

    async def check(mode):
        server = create_server(root, "brain")
        async with Client(
            server, mode=mode, client_info=Implementation(name="test-client", version="1")
        ) as client:
            status = data(await client.call_tool("mlca_status", {}))
            assert status["mode"] == "brain" and "inventory" not in status
            options = data(await client.call_tool("mlca_options", {}))
            assert options["catalog"] and options["options"][0]["id"].startswith("opt:")
            facts = data(await client.call_tool("mlca_read", {"kind": "facts", "ref": ""}))
            assert facts == {"facts_data": []}
            assert server.controller.session.principal == "agent:test-client/1"
            resource = await client.read_resource("mlca://view/status")
            assert resource.contents

    for mode in ("auto", "legacy"):
        asyncio.run(check(mode))
