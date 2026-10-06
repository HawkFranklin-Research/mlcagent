import asyncio
import json
import re

import pytest
import yaml
from mcp import Client
from mcp.types import Implementation

from mlca.api import Session
from mlca.llm.usage import read
from mlca.mcp.server import create_server
from tests.conftest import FIXTURES
from tests.helpers import advance_to
from tests.mcp.helpers import choose, data, poll


def script(action):
    responses = yaml.safe_load((FIXTURES / "synthetic_fake_llm.yaml").read_text())["responses"]
    text = next(r["text"] for r in responses if r.get("match", {}).get("action_id") == action)
    return re.fullmatch(r"\s*```(?:python)?\s*\n(.*?)\n```\s*", text, flags=re.S).group(1) + "\n"


async def submit(client, step_id, source):
    outcome = data(await client.call_tool("mlca_submit_script", {"step_id": step_id, "code": source}))
    if outcome["status"] in {"running", "starting"}:
        return await poll(client, step_id)
    return outcome


@pytest.mark.slow
def test_brain_full_path_zero_models(project_factory, monkeypatch):
    root = project_factory()
    server = create_server(root, "brain")
    monkeypatch.setattr(
        "mlca.llm.client.Client.complete", lambda *a, **kw: pytest.fail("Brain invoked a model")
    )

    async def check():
        async with Client(server, client_info=Implementation(name="brain-test", version="1")) as client:
            data(await client.call_tool("mlca_status", {}))
            s = server.controller.session
            s.config.roles.clear()
            s.config.providers.clear()
            figure = None
            for event in s.workflow.spec.events:
                assert s.state.current_event == event
                if event == "test":
                    req = data(
                        await client.call_tool(
                            "mlca_request_approval",
                            dict(kind="unlock_test", target="test", reason="planned test"),
                        )
                    )
                    with Session.open(root) as human:
                        human.resolve_approval(req["request_id"], "approved", "reviewed", "UNLOCK TEST")
                action = s.workflow.events[event].default_options[0]
                outcome = await choose(client, action)
                if not s.workflow.actions[action].builtin:
                    assert outcome["status"] == "awaiting_script"
                    assert not any(
                        str(root) in json.dumps(value)
                        for value in outcome["work_order"]["inputs_data"].values()
                    )
                    assert not list((root / ".mlca/data/exposed").glob("*"))
                    source = script(action)
                    if action == "audit_schema":
                        source += '\nimport matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.bar([0, 1], [2, 3])\nm.save_figure(fig, "summary.png")\n'
                        source += 'm.record_fact_candidate("row_count", 400, source="missing.json")\n'
                    outcome = await submit(client, outcome["step_id"], source)
                    assert outcome["status"] == "completed", outcome
                    if action == "audit_schema":
                        assert s.state.counts["FactRejected"] == 1
                        figure = next(
                            o["path"] for o in s.state.steps[-1]["figures"] if o["name"].endswith(".png")
                        )
                    assert not list((root / ".mlca/data/exposed").glob("*"))
                if event in {"onboard", "validate"}:
                    target = "brief_confirmed" if event == "onboard" else "model_selected"
                    req = data(
                        await client.call_tool(
                            "mlca_request_approval",
                            dict(kind="confirm", target=target, reason="review evidence"),
                        )
                    )
                    with Session.open(root) as human:
                        human.resolve_approval(req["request_id"], "approved", "reviewed")
                assert data(await client.call_tool("mlca_move", {"to": "next"}))
            reports = data(await client.call_tool("mlca_report", {"kind": "all"}))
            usage = json.loads((root / reports["paths_data"]["usage"]).read_text())
            assert usage["decisions_by_principal"]["user"] > 0
            assert usage["decisions_by_principal"]["agent:brain-test/1"] > 0
            assert usage["script_attempts_by_source"]["agent:brain-test/1"] > 0
            assert not [r for r in read(root) if r["role"] != "mcp"]
            image = await client.call_tool("mlca_read", {"kind": "figure", "ref": figure})
            assert image.content[1].type == "image"
            assert s.store.verify()["ok"]
            assert s.verify_scripts()["ok"]

    asyncio.run(check())


@pytest.mark.slow
def test_brain_bypasses_and_attempt_limit(project_factory, monkeypatch):
    root = project_factory()
    server = create_server(root, "brain")
    monkeypatch.setattr(
        "mlca.llm.client.Client.complete", lambda *a, **kw: pytest.fail("Model called on rejection")
    )

    async def check():
        async with Client(server) as client:
            menu = data(await client.call_tool("mlca_options", {}))
            option = menu["options"][0]
            raw = {
                k: option[k]
                for k in ("id", "action_id", "title", "why_now", "params", "advances", "expected_outputs")
            }
            for bad in [
                {**raw, "action_id": "not_in_catalog"},
                {**raw, "params": {"unknown": 1}},
                {**raw, "advances": ["unknown"]},
                {**raw, "event_done": True},
            ]:
                result = await client.call_tool("mlca_submit_options", {"options": [bad]})
                assert result.is_error, result
            accepted = data(await client.call_tool("mlca_submit_options", {"options": [raw]}))
            assert accepted["options"]
            assert (await client.call_tool("mlca_choose", {"option_id": option["id"]})).is_error
            assert (await client.call_tool("mlca_move", {"to": "next"})).is_error
            for text in ("use the test set", "Read /etc/passwd"):
                result = data(await client.call_tool("mlca_custom", {"text": text}))
                assert result["decision"] == "reject"
            await choose(client, "confirm_brief")
            req = data(
                await client.call_tool(
                    "mlca_request_approval", dict(kind="confirm", target="brief_confirmed", reason="reviewed")
                )
            )
            with Session.open(root) as human:
                human.resolve_approval(req["request_id"], "approved", "reviewed")
            assert (await client.call_tool("mlca_submit_options", {"options": [raw]})).is_error
            data(await client.call_tool("mlca_move", {"to": "next"}))
            pending = await choose(client, "audit_schema")
            assert (await client.call_tool("mlca_move", {"to": "next"})).is_error
            assert (
                await client.call_tool("mlca_submit_script", {"step_id": "wrong", "code": "print(1)"})
            ).is_error
            for i in range(3):
                result = await submit(client, pending["step_id"], "import socket")
                assert result["status"] == ("failed" if i == 2 else "awaiting_script")
            assert (
                await client.call_tool(
                    "mlca_submit_script", {"step_id": pending["step_id"], "code": "print(1)"}
                )
            ).is_error
            assert (
                await client.call_tool("mlca_read", {"kind": "table", "ref": "../synthetic.csv"})
            ).is_error
            assert server.controller.session.store.verify()["ok"]

    asyncio.run(check())


@pytest.mark.slow
def test_submitted_execution_guards(project_factory, sandbox_level):
    root = project_factory()
    with Session.open(root) as human:
        advance_to(human, "model")
    # Disguised path literals reach execution so namespace/audit refusals are exercised too.
    from mlca.paths import user_data_dir

    with Session.open(root) as snapshot:
        targets = [
            root / snapshot.state.split["vault"]["path"],
            root.parent / "synthetic.csv",
            next((user_data_dir() / "keys").glob("*.key")),
        ]
    malicious = [
        "import socket",
        "from sklearn.linear_model import LogisticRegression\nLogisticRegression().fit([[0],[1]],[0,1])",
        script("train_logistic").replace('i["val"]', 'i["val"]'),
    ]
    fitting = script("train_logistic")
    malicious[2] = fitting.replace('m.inputs()["train"]', 'm.inputs()["val"]')
    malicious.append('from pathlib import Path\nPath("escape.txt").write_text("bad")\n' + fitting)
    for target in targets:
        encoded = [ord(c) for c in str(target)]
        malicious.append(f'open("".join(chr(n) for n in {encoded}), "rb").read()\n' + fitting)

    async def check():
        server = create_server(root, "brain")
        async with Client(server) as client:
            for source in malicious:
                pending = await choose(client, "train_logistic")
                outcome = await submit(client, pending["step_id"], source)
                assert outcome["status"] == "awaiting_script", outcome
                server.controller.session.abandon_step(pending["step_id"], "guard regression complete")
            pending = await choose(client, "train_logistic")
            outcome = await submit(client, pending["step_id"], fitting)
            assert outcome["status"] == "completed", outcome
            assert (
                await client.call_tool("mlca_submit_script", {"step_id": pending["step_id"], "code": fitting})
            ).is_error

    asyncio.run(check())
