from mlca.api import Session
from mlca.llm.client import RequestContext
from mlca.llm.usage import read


def test_lazy_snapshot_and_reported_model(project_factory, monkeypatch):
    monkeypatch.setenv("CANARY_TOKEN", "snapshot-secret-canary")
    root = project_factory(
        responses=[
            {
                "match": {"role": "worker", "purpose": "snapshot"},
                "text": "ok",
                "model_reported": "actual-model",
            }
        ]
    )
    with Session.open(root) as session:
        assert not any(r.type.value == "RunSnapshot" for r in session.store.read())
        session.emit("Note", {"text": "snapshot-secret-canary"})
        session.emit("Note", {"text": "second mutation"})
        snapshots = [r for r in session.store.read() if r.type.value == "RunSnapshot"]
        assert len(snapshots) == 1
        assert snapshots[0].payload["roles"]["worker"]["model"] == "scripted"
        assert snapshots[0].payload["template"]["sha256"] == session.workflow.sha256
        assert snapshots[0].payload["environment_lock_sha256"] == session.state.lock_sha256
        assert "snapshot-secret-canary" not in session.store.path.read_text()
        session.client.complete(
            "worker",
            [],
            context=RequestContext(role="worker", session_id=session.session_id, purpose="snapshot"),
            categories=[],
        )
        usage = read(root)[0]
        assert usage["model_reported"] == "actual-model"
        assert usage["request_settings"]["max_output_tokens"] == 16384
