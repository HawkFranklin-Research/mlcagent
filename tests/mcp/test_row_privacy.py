import asyncio
import json

import pandas as pd
import pytest
from mcp import Client

from mlca.api import Session
from mlca.mcp.server import create_server
from tests.helpers import advance_to
from tests.mcp.helpers import choose, data
from tests.mcp.test_brain import submit


@pytest.mark.parametrize("raw", [True, False])
def test_head_rows_refused_describe_readable(project_factory, raw):
    root = project_factory()
    with Session.open(root) as human:
        advance_to(human, "eda")
    server = create_server(root, "brain")

    async def check():
        async with Client(server) as client:
            pending = await choose(client, "describe_distributions")
            table = "df.head(8)" if raw else "df.describe().reset_index()"
            source = f"""import pandas as pd, mlca_runtime as m
df = pd.read_csv(list(m.inputs().values())[0])
m.save_table({table}, "distributions.csv")
m.record_fact_candidate("n_numeric", df.iloc[0].to_dict(), source="distributions.csv")
print("STDOUT_ROW_CANARY", df.iloc[0].to_dict())
"""
            if raw:
                source += (
                    'm.save_table(df.head(8)[["y", "x1"]].round(5).assign(extra="ignored"), "subset.csv")\n'
                )
            completed = await submit(client, pending["step_id"], source)
            assert completed["status"] == "completed", completed
            session = server.controller.session
            assert session.state.counts["FactRejected"] >= 1
            assert "n_numeric" not in session.state.facts
            assert any(
                r.type.value == "FactRejected" and "registered data row" in r.payload["reason"]
                for r in session.store.read()
            )
            for suffix in ("csv", "parquet"):
                ref = next(
                    path for path in session.state.artefacts if path.endswith("distributions." + suffix)
                )
                assert session.state.artefacts[ref]["contains_data_rows"] is raw
                result = await client.call_tool("mlca_read", {"kind": "table", "ref": ref})
                if raw:
                    assert result.is_error and "data rows" in result.content[0].text
                    sample = pd.read_csv(root.parent / "synthetic.csv").iloc[0].to_json()
                    assert sample not in result.content[0].text
                else:
                    assert len(data(result)["table_data"]) == 8
            data(await client.call_tool("mlca_report", {"kind": "all"}))
            report = json.loads((root / "reports/generated/trust_boundary.json").read_text())
            assert report["agent_file_access"] == "unknown (outside MLCA)"
            assert bool(report["contains_data_rows"]) is raw
            provenance = json.loads((root / "reports/generated/provenance.json").read_text())
            assert all(entry["agent_file_access"] == "unknown (outside MLCA)" for entry in provenance)
            response = await client.call_tool("mlca_read", {"kind": "report", "ref": "provenance"})
            assert not response.is_error, response
            assert "STDOUT_ROW_CANARY" not in response.content[0].text
            if raw:
                subset = next(path for path in session.state.artefacts if path.endswith("subset.csv"))
                result = await client.call_tool("mlca_read", {"kind": "table", "ref": subset})
                assert result.is_error and "data rows" in result.content[0].text
            # Legacy metadata cannot bypass the read-time check.
            if raw:
                for output in session.state.artefacts.values():
                    output.pop("contains_data_rows", None)
                result = await client.call_tool("mlca_read", {"kind": "table", "ref": ref})
                assert result.is_error
            session.config.privacy.allow_sample_rows = True
            result = await client.call_tool("mlca_read", {"kind": "table", "ref": ref})
            assert not result.is_error

    asyncio.run(check())


def test_legacy_fact_views_refused_and_private_store_not_readable(project_factory):
    root = project_factory()
    row = pd.read_csv(root.parent / "synthetic.csv").iloc[0].to_dict()
    with Session.open(root) as human:
        human.emit(
            "FactRecorded",
            {"key": "legacy_raw", "value": row, "source": "legacy", "sha256": "old", "step_id": "legacy"},
        )
    server = create_server(root, "brain")

    async def check():
        async with Client(server) as client:
            for tool, arguments in (
                ("mlca_status", {}),
                ("mlca_read", {"kind": "facts", "ref": ""}),
                ("mlca_read", {"kind": "table", "ref": ".mlca/private/row_fingerprints"}),
            ):
                result = await client.call_tool(tool, arguments)
                assert result.is_error and "data row" in result.content[0].text
                assert str(row["x1"]) not in result.content[0].text

    asyncio.run(check())


def test_private_fingerprints_unreadable_by_step(project_factory, sandbox_level):
    root = project_factory()
    with Session.open(root) as human:
        advance_to(human, "data")
    path = root / ".mlca/private/row_fingerprints"
    encoded = ",".join(str(ord(char)) for char in str(path))
    server = create_server(root, "brain")

    async def check():
        async with Client(server) as client:
            pending = await choose(client, "audit_schema")
            source = f'p="".join(chr(i) for i in [{encoded}])\nopen(p,"rb").read()\n'
            result = await submit(client, pending["step_id"], source)
            assert result["status"] == "awaiting_script"
            assert server.controller.session.state.steps[-1]["runs"][-1]["exit_status"] != 0
            with Session.open(root) as human:
                human.abandon_step(pending["step_id"], "privacy probe finished")

    asyncio.run(check())
