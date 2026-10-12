import json

import pytest
from typer.testing import CliRunner

from mlca.api import Session
from mlca.cli.main import app
from mlca.errors import IntegrityError
from mlca.log.replay import replay
from tests.helpers import advance_to, choose_action


@pytest.mark.slow
def test_default_path(project_factory, sandbox_level):
    root = project_factory()
    with Session.open(root) as session:
        advance_to(session, "test")
        session.unlock_test("UNLOCK TEST")
        choose_action(session, "score_test")
        session.next()
        choose_action(session, "explain_model")
        session.next()
        choose_action(session, "generate_reports")
        assert session.next() == {"complete": True}
        assert all(value == "done" for value in session.state.event_statuses.values())
        assert session.store.verify()["ok"]
        assert replay(session.branches.records()) == session.state
        usage = [json.loads(line) for line in (root / ".mlca/usage.jsonl").read_text().splitlines()]
        egress = [json.loads(line) for line in (root / ".mlca/egress.jsonl").read_text().splitlines()]
        assert len(usage) == len(egress) > 0
        assert {u["request_id"] for u in usage} == {e["request_id"] for e in egress}
        reports = session.report()
        assert reports and all((root / path).exists() for path in reports.values())
        verified = session.verify_scripts()
        assert verified["ok"], verified
        assert verified["fresh_environment"]


@pytest.mark.slow
def test_readonly_cli_and_state_cache(project_factory, monkeypatch):
    root = project_factory()
    with Session.open(root) as session:
        first = session.state
        with monkeypatch.context() as patch:
            patch.setattr("mlca.api.replay", lambda *_: pytest.fail("Repeated replay of unchanged head"))
            assert session.state is first
    count = len(Session.open(root).store.read())
    runner = CliRunner()
    for command in ("status", "log", "usage", "branches", "doctor", "templates list"):
        result = runner.invoke(app, ["--project", str(root), *command.split(), "--json"])
        assert result.exit_code == 0, result.output
        assert len(Session.open(root).store.read()) == count


@pytest.mark.slow
def test_new_session_detects_old_edit(project_factory):
    root = project_factory()
    with Session.open(root) as session:
        session.store.read()
        lines = session.store.path.read_text().splitlines()
        record = json.loads(lines[0])
        record["payload"]["project_id"] = "modified"
        lines[0] = json.dumps(record)
        session.store.path.write_text("\n".join(lines) + "\n")
        with pytest.raises(IntegrityError):
            session.store.verify()
    with pytest.raises(IntegrityError):
        Session.open(root)
    result = CliRunner().invoke(app, ["--project", str(root), "log", "--verify"])
    assert isinstance(result.exception, IntegrityError)


@pytest.mark.slow
def test_exhausted_event_explains_custom(project_factory):
    root = project_factory()
    with Session.open(root) as session:
        choose_action(session, "confirm_brief")
        options = session.options()
        assert len(options) == 1 and options[0]["id"] == "custom"
        assert "remaining study decisions" in options[0]["note"]
        assert "scoped instruction" in options[0]["note"]
        assert "exhausted" not in options[0]["note"].lower()


@pytest.mark.slow
def test_survival_init_resolves_columns(project_factory):
    root = project_factory(template="survival", brief={"target": "DURATION", "event_column": "OBSERVED"})
    with Session.open(root) as session:
        assert session.state.columns == {
            "target": "duration",
            "duration": "duration",
            "event_column": "observed",
        }
        choose_action(session, "confirm_brief")
        payload = json.loads((root / session.state.steps[0]["outputs"][0]["path"]).read_text())
        assert payload["columns"] == session.state.columns
