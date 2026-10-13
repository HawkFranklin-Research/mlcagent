import asyncio
import json

from mcp import Client
from mcp.types import Implementation

from mlca.mcp.server import create_server
from tests.mcp.helpers import data


def test_human_cards_have_owner_route_and_specific_refusal(project_factory):
    root = project_factory(brief={"target": "", "unit": "", "aim": "Predict outcome"})
    server = create_server(root, "brain")

    async def check():
        async with Client(server, client_info=Implementation(name="cards", version="1")) as client:
            menu = data(await client.call_tool("mlca_options", {}))
            assert all(o["actor"] in {"human", "agent", "engine"} for o in menu["options"])
            human = next(o for o in menu["options"] if o["actor"] == "human")
            assert human["id"].split(":", 2)[2] == "human:study"
            assert human["how"]["kind"] == "study_fields"
            response = await client.call_tool("mlca_choose", {"option_id": human["id"]})
            assert response.is_error
            result = json.loads(response.content[0].text)["data"]
            assert result["category"] == "human_decision"
            assert result["how"] == human["how"]
            assert "stale" not in result["error_data"].lower()
            assert any(
                r.type.value == "Refusal" and r.payload["category"] == "human_decision"
                for r in server.controller.session.store.read()
            )

    asyncio.run(check())
