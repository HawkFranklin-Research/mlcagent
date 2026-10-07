from mlca.api import Session
from mlca.roles.worker import Worker
from tests.helpers import advance_to, choose_action


def test_driver_fallback_supporting_after_completion(project_factory, monkeypatch):
    with Session.open(project_factory()) as session:
        advance_to(session, "data")
        session.config.roles.pop("navigator", None)
        assert [o.get("action_id") for o in session.options()[:2]] == ["audit_schema", "count_target"]
        choose_action(session, "audit_schema")
        assert session.state.event_statuses["data"] == "done"
        generation = session.state.generations["data"]
        menu = session.options()
        assert menu[0]["id"] == "next" and menu[-1]["id"] == "custom"
        source = """import pandas as pd, mlca_runtime as m
df = pd.read_csv(list(m.inputs().values())[0])
counts = df.y.value_counts().rename_axis("class").reset_index(name="n")
counts["share"] = counts.n / len(df)
m.save_table(counts, "target_counts.csv")
"""
        monkeypatch.setattr(Worker, "write_script", lambda *a, **kw: (source, "offline-test"))
        choose_action(session, "count_target")
        assert session.state.event_statuses["data"] == "done"
        assert session.state.generations["data"] == generation
        assert [o["id"] for o in session.options()] == ["next", "custom"]
        assert session.next()["event"] == "eda"
