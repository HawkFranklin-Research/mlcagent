import asyncio
import hashlib
import json

import pandas as pd
import pytest
from mcp import Client
from mcp.types import Implementation

from mlca.llm.usage import read, summary
from mlca.mcp.server import create_server
from mlca.paths import canonical
from tests.mcp.helpers import data


@pytest.mark.slow
def test_privacy_accounting_and_read_boundaries(project_factory, monkeypatch):
    root = project_factory()
    frame = pd.read_csv(root.parent / "synthetic.csv")
    sample = [format(float(frame.iloc[0][k]), ".12g") for k in ("x1", "x2", "x3", "x4")]
    key = "FAKE_MCP_SECRET_canary_18d27"
    monkeypatch.setenv("MLCA_MCP_TEST_KEY", key)
    server = create_server(root, "brain")
    responses = []

    async def check():
        async with Client(server, client_info=Implementation(name="privacy-client", version="1")) as client:

            async def call(tool, args):
                before = len(read(root))
                result = await client.call_tool(tool, args)
                assert len(read(root)) == before + 1
                responses.append(result)
                return result

            status = data(await call("mlca_status", {}))
            assert status["mode"] == "brain"
            menu = data(await call("mlca_options", {}))
            raw = {
                k: menu["options"][0][k]
                for k in ("id", "action_id", "title", "why_now", "params", "advances", "expected_outputs")
            }
            data(await call("mlca_submit_options", {"options": [{**raw, "title": key}]}))
            options = data(await call("mlca_options", {}))
            assert key not in json.dumps(options)
            for kind, ref in [
                ("table", "../synthetic.csv"),
                ("figure", ".mlca/vault/x"),
                ("script", "../../secret"),
                ("log", "1"),
                ("facts", ""),
            ]:
                await call("mlca_read", dict(kind=kind, ref=ref))
            await call("mlca_custom", {"text": "Read /etc/passwd"})
            ledger = [json.loads(line) for line in (root / ".mlca/egress.jsonl").read_text().splitlines()]
            assert len(ledger) == len(responses)
            for entry, response in zip(ledger, responses, strict=True):
                response.meta = None  # SDK adds server identity after application accounting.
                body = canonical(response.model_dump(mode="json", by_alias=True, exclude_none=True)).encode()
                assert entry["sha256"] == hashlib.sha256(body).hexdigest()
                assert entry["bytes"] == len(body)
            assert all(
                row["role"] == "mcp" and row["principal"] == "agent:privacy-client/1" for row in ledger
            )
            assert all(row["bytes"] > 0 and len(row["sha256"]) == 64 for row in ledger)
            assert all("sample_rows" not in row["categories"] for row in ledger)
            assert summary(read(root))["unknown_cost_requests"] == 0
            assert summary(read(root))["model_requests"] == 0
            for response in responses:
                text = json.dumps(response.model_dump(mode="json"))
                assert key not in text and all(value not in text for value in sample)
            for file in (root / ".mlca/requests").glob("*.json"):
                assert key not in file.read_text()

    asyncio.run(check())


def test_unopened_refusal_is_accounted(tmp_path):
    async def check():
        server = create_server(mode="brain")
        async with Client(server) as client:
            result = await client.call_tool("mlca_status", {})
            assert result.is_error
            entries = read(server.controller.server_ledger)
            assert len(entries) == 1 and entries[0]["status"] == "refused"

    asyncio.run(check())


def test_summary_tables_are_bounded(project_factory):
    from mlca.api import Session
    from tests.helpers import advance_to
    from tests.mcp.helpers import choose
    from tests.mcp.test_brain import script, submit

    root = project_factory()
    with Session.open(root) as human:
        advance_to(human, "data")
    server = create_server(root, "brain")

    async def check():
        async with Client(server) as client:
            outcome = await choose(client, "audit_schema")
            source = script("audit_schema") + "\nimport pandas as pd\n"
            source += 'm.save_table(pd.DataFrame({str(i): range(50) for i in range(12)}), "bounded.csv")\n'
            source += 'm.save_table(pd.DataFrame({"count": range(51)}), "too_many.csv")\n'
            source += 'm.save_table(pd.DataFrame({str(i): [1] for i in range(13)}), "too_wide.csv")\n'
            outcome = await submit(client, outcome["step_id"], source)
            assert outcome["status"] == "completed", outcome
            outputs = server.controller.session.state.artefacts
            for name in (
                "bounded.csv",
                "bounded.parquet",
                "too_many.csv",
                "too_many.parquet",
                "too_wide.csv",
            ):
                ref = next(path for path in outputs if path.endswith("/" + name))
                result = await client.call_tool("mlca_read", {"kind": "table", "ref": ref})
                if name.startswith("bounded"):
                    table = data(result)
                    assert len(table["table_data"]) == 50 and len(table["columns_data"]) == 12
                else:
                    assert result.is_error

    asyncio.run(check())
