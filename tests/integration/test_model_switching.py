import pytest

from mlca.api import Session
from mlca.config import Config
from mlca.errors import MlcaUserError


def alternative(session):
    data = session.config.model_dump()
    data["roles"]["worker"]["model"] = "alternative"
    return Config.model_validate(data)


def test_switch_reopens_and_is_reported(opened_project):
    session = opened_project
    session.change_models(alternative(session))
    records = [r for r in session.store.read() if r.type.value == "ModelChanged"]
    assert records[0].actor == "user"
    assert records[0].payload["to"]["model"] == "alternative"
    with Session.open(session.root) as reopened:
        assert reopened.config.roles["worker"].model == "alternative"
        from mlca.evaluation.metrics import build

        assert build(reopened)["model_changes"][0]["to"]["model"] == "alternative"


def test_bench_model_lock_and_agent_refusal(opened_project):
    session = opened_project
    session.lock_models()
    with pytest.raises(MlcaUserError, match="locked"):
        session.change_models(alternative(session))
    session.principal = "agent:test/1"
    with pytest.raises(MlcaUserError, match="human"):
        session.change_models(alternative(session))
