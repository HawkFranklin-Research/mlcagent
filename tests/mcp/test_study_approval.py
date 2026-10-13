import asyncio

import pytest
from mcp import Client
from mcp.types import Implementation
from typer.testing import CliRunner

from mlca.api import Session
from mlca.cli.main import app
from mlca.errors import MlcaUserError
from mlca.mcp.server import create_server
from tests.mcp.helpers import data


def test_agent_proposal_human_cli_edit_and_attribution(project_factory, monkeypatch):
    root = project_factory(brief={"target": "", "unit": "", "aim": "Predict"})
    server = create_server(root, "brain")

    async def propose():
        async with Client(server, client_info=Implementation(name="proposer", version="1")) as client:
            return data(
                await client.call_tool(
                    "mlca_request_approval",
                    {
                        "kind": "study_fields",
                        "target": "onboard",
                        "reason": "Choose outcome",
                        "proposed": {"target": "y", "unit": "sample"},
                    },
                )
            )

    requested = asyncio.run(propose())
    with Session.open(root) as human:
        assert human.state.columns["target"] is None
        assert human.approvals()[0]["proposed"]["target"] == "y"
    monkeypatch.setattr("mlca.cli.main.edit_text", lambda *_: '{"target":"y","unit":"patient"}')
    result = CliRunner().invoke(
        app, ["-p", str(root), "approvals", "approve", requested["request_id"], "--edit"]
    )
    assert result.exit_code == 0, result.output
    with Session.open(root) as human:
        assert human.state.columns["target"] == "y"
        assert human.state.brief["unit"] == "patient"
        record = next(r for r in human.store.read() if r.type.value == "StudyFieldsResolved")
        assert record.actor == "user"
        assert record.payload["proposer"] == "agent:proposer/1"
        assert record.payload["decider"] == "user"


def test_decline_and_invalid_proposal_do_not_apply(project_factory):
    root = project_factory(brief={"target": "", "unit": "", "aim": "Predict"})
    with Session.open(root, principal="agent:test/1", mode="brain") as agent:
        with pytest.raises(MlcaUserError, match="Unresolved"):
            agent.request_approval("study_fields", "onboard", "Choose", {"target": "invented"})
        assert agent.approvals() == []
        request = agent.request_approval("study_fields", "onboard", "Choose", {"target": "y"})
    with Session.open(root) as human:
        before = human.state.columns.copy()
        human.resolve_approval(request["request_id"], "declined")
        assert human.state.columns == before
        assert human.approvals() == []
