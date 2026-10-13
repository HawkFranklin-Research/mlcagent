import asyncio
import json

from mcp import Client
from mcp.types import Implementation

from mlca.api import Session
from mlca.evaluation.metrics import build
from mlca.mcp.server import create_server
from mlca.report.usage_report import build as report
from tests.mcp.helpers import choose, data, poll
from tests.mcp.test_brain import script


def test_synthetic_brain_approval_sources_and_wait_metrics(project_factory):
    root = project_factory(brief={"target": "", "unit": "", "aim": "Predict outcome"})
    server = create_server(root, "brain")

    async def check():
        async with Client(server, client_info=Implementation(name="metric-agent", version="1")) as client:
            menu = data(await client.call_tool("mlca_options", {}))
            human_card = next(o for o in menu["options"] if o["actor"] == "human")
            refused = await client.call_tool("mlca_choose", {"option_id": human_card["id"]})
            assert refused.is_error
            request = data(
                await client.call_tool(
                    "mlca_request_approval",
                    {
                        "kind": "study_fields",
                        "target": "onboard",
                        "reason": "Select outcome",
                        "proposed": {"target": "y", "unit": "sample"},
                    },
                )
            )
            with Session.open(root) as human:
                human.resolve_approval(request["request_id"], "approved")
            await choose(client, "confirm_brief")
            request = data(
                await client.call_tool(
                    "mlca_request_approval",
                    {"kind": "confirm", "target": "brief_confirmed", "reason": "Review brief"},
                )
            )
            with Session.open(root) as human:
                human.resolve_approval(request["request_id"], "approved", "Reviewed")
            data(await client.call_tool("mlca_move", {"to": "next"}))
            outcome = await choose(client, "audit_schema")
            data(
                await client.call_tool(
                    "mlca_submit_script", {"step_id": outcome["step_id"], "code": script("audit_schema")}
                )
            )
            assert (await poll(client, outcome["step_id"]))["status"] == "completed"

    asyncio.run(check())
    with Session.open(root) as human:
        metrics = build(human)
        assert metrics["run"]["mode"] == "brain"
        brain = metrics["brain_mode"]
        assert brain["agent_requested_approvals"]["value"] == 2
        assert brain["human_approval_wait_s"]["value"] >= 0
        assert brain["agent_script_steps"]["value"] == 1
        assert brain["agent_script_step_share"]["value"] == 0.5
        assert metrics["interventions"]["agent:metric-agent/1"]["study_fields_proposed"]["value"] == 1
        assert metrics["interventions"]["agent:metric-agent/1"]["human_decision_refusals"]["value"] == 1
        assert metrics["study_proposals"][0]["decider"] == "user"
        result = report(human.state, [], human.branches.records())
        assert result["human_decision_refusals_by_principal"] == {"agent:metric-agent/1": 1}
        assert result["study_proposals"][0]["proposer"] == "agent:metric-agent/1"
        assert json.dumps(result)
