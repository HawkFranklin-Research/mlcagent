from mlca.api import Session
from mlca.evaluation.metrics import generate
from tests.helpers import advance_to, choose_action


def test_driver_metrics_golden(project_factory, monkeypatch):
    with Session.open(project_factory()) as session:
        advance_to(session, "test")
        session.unlock_test("UNLOCK TEST")
        choose_action(session, "score_test")
        session.next()
        choose_action(session, "explain_model")
        session.next()
        choose_action(session, "generate_reports")
        count = len(session.store.read())
        monkeypatch.setattr(
            session.client, "complete", lambda *a, **k: (_ for _ in ()).throw(AssertionError("model call"))
        )
        metrics = generate(session)
        assert metrics["run"]["completed"]["value"] is True
        assert metrics["steps"]["count"]["value"] == 11
        assert metrics["results"]["test"]["value"]["value"] is not None
        assert metrics["provenance"]["coverage"]["value"] == 1.0
        assert metrics["models"]["worker"]["cost_usd"]["value"] == 0.0
        assert metrics["time"]["human_active_s"]["source"] == "unavailable"
        assert len(session.store.read()) == count
        assert (session.root / "reports/generated/metrics.json").exists()


def test_brain_metrics_unknown_external_usage(project_factory):
    with Session.open(project_factory(), mode="brain", principal="agent:fixture/1") as session:
        session.options()
        metrics = generate(session)
        assert metrics["models"]["external_agent"] == {"value": None, "source": "unavailable"}
        assert metrics["run"]["mode"] == "brain"
        assert metrics["results"]["test"]["value"]["value"] is None


def test_recovery_and_unknown_usage(project_factory, monkeypatch):
    import pytest

    from mlca.errors import MlcaUserError
    from mlca.llm.client import RequestContext

    bad = {
        "match": {"role": "worker", "action_id": "audit_schema", "purpose": "write"},
        "text": "```python\nimport socket\n```",
    }
    with Session.open(project_factory(responses=[bad])) as session:
        advance_to(session, "data")
        choose_action(session, "audit_schema")
        metrics = generate(session)
        assert metrics["recovery"]["automatic"]["value"] == 1
        assert metrics["failures"]["static_check"]["value"] == 1
        assert metrics["egress"]["bytes"]["value"] > 0

        class Broken:
            def complete(self, *args):
                raise ValueError("provider broke")

        monkeypatch.setattr(session.client, "_provider", lambda *_: Broken())
        with pytest.raises(MlcaUserError):
            session.client.complete(
                "worker",
                [],
                context=RequestContext(role="worker", session_id=session.session_id),
                categories=[],
            )
        result = generate(session)
        assert result["models"]["worker"]["input_tokens"]["value"] is None
        assert result["models"]["worker"]["cost_usd"]["source"] == "unavailable"
