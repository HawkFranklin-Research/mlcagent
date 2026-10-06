import pytest

from mlca.api import Session
from mlca.errors import MlcaUserError
from tests.helpers import choose_action


@pytest.mark.slow
def test_agent_refusals_and_human_approvals(project_factory):
    root = project_factory()
    with Session.open(root, principal="agent:test/1", mode="brain") as s:
        for function in [
            lambda: s.confirm("brief_confirmed", "yes"),
            lambda: s.unlock_test("UNLOCK TEST"),
            lambda: s.package("numpy", True),
            lambda: s.resolve_approval("bad", "approved"),
        ]:
            with pytest.raises(MlcaUserError, match="human author"):
                function()
        choose_action(s, "confirm_brief")
        request = s.request_approval("confirm", "brief_confirmed", "Please review the brief")
        declined = s.request_approval("package", "numpy", "not needed")
    with Session.open(root) as human:
        human.resolve_approval(declined["request_id"], "declined", "not needed")
        human.resolve_approval(request["request_id"], "approved", "reviewed")
        assert human.state.event_statuses["onboard"] == "done"
        assert human.approvals() == []
        records = human.store.read()
        assert next(r for r in records if r.type.value == "OptionChosen").actor == "agent:test/1"
        assert next(r for r in records if r.type.value == "UserConfirmed").actor == "user"


@pytest.mark.slow
def test_external_steps_resume_and_limit(project_factory, monkeypatch):
    root = project_factory()
    with Session.open(root, principal="agent:test/1", mode="brain") as s:
        monkeypatch.setattr(s.client, "complete", lambda *a, **kw: pytest.fail("Brain made a model call"))
        choose_action(s, "confirm_brief")
    with Session.open(root) as human:
        human.confirm("brief_confirmed", "reviewed")
        human.next()
    with Session.open(root, principal="agent:test/1", mode="brain") as s:
        option = s.options()[0]
        result = s.choose(option["id"])
        step_id = result["step_id"]
        assert result["status"] == "awaiting_script"
        assert "worker_prompt" in result["work_order"]
        for function in [lambda: s.next(), lambda: s.choose("1"), lambda: s.branch("bad", s.state.head)]:
            with pytest.raises(MlcaUserError, match="awaiting_script"):
                function()
    with Session.open(root, principal="agent:test/1", mode="brain") as s:
        assert s.step_status(step_id)["attempt"] == 1
        for attempt in range(1, 4):
            result = s.submit_script(step_id, "import socket")
            assert result["status"] == ("failed" if attempt == 3 else "awaiting_script")
        with pytest.raises(MlcaUserError, match="not awaiting"):
            s.submit_script(step_id, "print(1)")
        assert s.store.verify()["ok"]
