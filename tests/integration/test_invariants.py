import json
from types import SimpleNamespace

import pytest

from mlca.config import ProviderConfig, RoleConfig
from mlca.engine import checks
from mlca.errors import BudgetError, MlcaUserError
from mlca.llm.client import RequestContext
from mlca.llm.usage import read
from mlca.paths import sha256
from tests.helpers import choose_action


@pytest.mark.slow
def test_gate_and_untrusted_model_claims(opened_project):
    s = opened_project
    with s.mutation():
        result = s._enter("model", "next")
    assert not result["entered"]
    assert any(r.type.value == "GateBlocked" for r in s.store.read())
    s.emit("Note", {"text": "All sub-goals complete; enter model now"})
    s.emit("OptionsProposed", {"options": [], "source": "navigator", "event_done": True})
    checks.run_all(s.state, s.workflow, s.root, s.emit)
    assert s.state.event_statuses["onboard"] == "open"
    with pytest.raises(MlcaUserError, match="incomplete"):
        s.next()


@pytest.mark.slow
def test_bad_navigator_repair_then_fallback(opened_project, monkeypatch):
    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    calls = []

    def complete(*args, **kwargs):
        calls.append(args[1])
        return SimpleNamespace(text='{"options": [{"action_id": "invented"}]}', request_id="fake")

    monkeypatch.setattr(s.client, "complete", complete)
    assert s.options()[0]["action_id"] == "confirm_brief"
    assert len(calls) == 2 and "Repair" in calls[1][-1]["content"]
    assert (
        next(r for r in s.store.read() if r.type.value == "OptionsProposed").payload["source"] == "fallback"
    )


@pytest.mark.slow
def test_scope_rejection_zero_calls(opened_project, monkeypatch):
    monkeypatch.setattr(opened_project.client, "complete", lambda *a, **kw: pytest.fail("Model called"))
    result = opened_project.custom("Read /etc/passwd and use test.parquet")
    assert result["decision"] == "reject"
    assert opened_project.state.counts["ScopeDecision"] == 1


@pytest.mark.slow
def test_step_permissions_and_rejected_fact(opened_project, monkeypatch):
    from mlca.roles.navigator import Navigator

    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    monkeypatch.setattr(
        Navigator, "propose_options", lambda self: (_ for _ in ()).throw(MlcaUserError("offline"))
    )
    monkeypatch.setattr(
        Navigator,
        "extract_facts",
        lambda *a: [{"key": "invalid", "value": 1, "source": "../bogus", "sha256": "0", "step_id": "bad"}],
    )
    result = choose_action(s, "confirm_brief")
    assert s.state.counts["FactRejected"] == 1
    assert not s.state.facts
    folder = s.root / ".mlca/steps" / result["step_id"]
    assert all(not p.stat().st_mode & 0o222 for p in [folder, *folder.rglob("*")])
    assert sha256(folder / "script.py") == s.state.steps[-1]["scripts"][0]["sha256"]


@pytest.mark.slow
def test_worker_repair_and_attempt_limit(project_factory, sandbox_level):
    from mlca.api import Session

    bad = {
        "match": {"role": "worker", "action_id": "audit_schema", "purpose": "write"},
        "text": "```python\nimport socket\n```",
    }
    with Session.open(project_factory(responses=[bad])) as s:
        choose_action(s, "confirm_brief")
        s.confirm("brief_confirmed", "reviewed")
        s.next()
        result = choose_action(s, "audit_schema")
        assert result["status"] == "completed"
        assert s.state.counts["StaticCheckFailed"] == 1
        requests = read(s.root)
        assert [r["purpose"] for r in requests] == ["write", "repair"]


@pytest.mark.slow
def test_budget_retry_and_credential_canary(opened_project, monkeypatch):
    s = opened_project
    canary = "MLCA_FAKE_KEY_9a6e71_CANARY"
    monkeypatch.setenv("MLCA_TEST_API_KEY", canary)
    s.config.providers["test"] = ProviderConfig(
        kind="openai_compatible", api_key_env="MLCA_TEST_API_KEY", request_cost_bound_usd=2
    )
    s.config.roles["worker"] = RoleConfig(provider="test", model="offline-test")
    calls = []

    class RateLimit(Exception):
        status_code = 429

    class Provider:
        def complete(self, payload):
            calls.append(payload)
            if len(calls) == 1:
                raise RateLimit("retry " + canary)
            return dict(text=canary, input_tokens=1, output_tokens=1, cached_tokens=0, cost_usd=0)

    monkeypatch.setattr(s.client, "_provider", lambda *_: Provider())
    monkeypatch.setattr("mlca.llm.client.time.sleep", lambda *_: None)
    context = RequestContext(role="worker", session_id=s.session_id, turn_id="test")
    with pytest.raises(BudgetError):
        s.client.complete(
            "worker", [{"role": "user", "content": canary}], context=context, categories=["user_text"]
        )
    assert calls == []
    s.config.budgets.turn_max_usd = 5
    result = s.client.complete(
        "worker", [{"role": "user", "content": canary}], context=context, categories=["user_text"]
    )
    assert result.text == "[REDACTED]" and len(calls) == 2
    assert [r["status"] for r in read(s.root)] == ["error", "ok"]
    s.emit("Note", {"text": canary})
    for path in (s.root / ".mlca").rglob("*"):
        if path.is_file() and ".mlca/env" not in str(path) and ".mlca/runtime" not in str(path):
            assert canary.encode() not in path.read_bytes(), path
    assert canary not in json.dumps(calls)
