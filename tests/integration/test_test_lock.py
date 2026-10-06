import pytest

from mlca.api import Session
from mlca.errors import MlcaUserError
from mlca.runner.run_step import run_step
from tests.helpers import advance_to, choose_action


@pytest.mark.slow
def test_test_lock_cleanup_and_loop(project_factory, sandbox_level):
    with Session.open(project_factory()) as session:
        advance_to(session, "test")
        folders = set((session.root / ".mlca/steps").iterdir())
        with pytest.raises(MlcaUserError, match="locked test"):
            run_step(session, session.workflow.actions["score_test"], {})
        assert set((session.root / ".mlca/steps").iterdir()) == folders
        session.unlock_test("UNLOCK TEST")
        choose_action(session, "score_test")
        assert not list((session.root / ".mlca/data/exposed").iterdir())
        with pytest.raises(MlcaUserError):
            session.loop("model")
        session.branch(
            "before-exposure", next(s for s in session.state.steps if s["event_id"] == "model")["step_id"]
        )
        with pytest.raises(MlcaUserError, match="closed after project-wide test exposure"):
            from mlca.engine.turn import execute

            execute(session, session.workflow.actions["train_alternative"], {})
