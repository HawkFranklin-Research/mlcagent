import pytest
from conftest import advance_to, choose_action

from mlca.api import Session


@pytest.mark.slow
def test_branch_rechecks_and_checkout(project_factory, sandbox_level):
    with Session.open(project_factory()) as session:
        advance_to(session, "model")
        completed = choose_action(session, "train_logistic")
        session.next()
        main_event = session.state.current_event
        session.branch("alternative", completed["step_id"])
        assert session.state.current_event == "model"
        assert session.state.event_statuses["model"] == "done"
        assert all(
            session.state.subgoals["model." + s.id]["passed"]
            for s in session.workflow.events["model"].subgoals
        )
        options = session.options()
        assert any(o["id"] == "next" for o in options)
        assert not any(o.get("action_id") for o in options)
        session.checkout("main")
        assert session.state.current_event == main_event
        assert session.state.event_statuses["model"] == "done"
