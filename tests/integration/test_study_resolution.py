import pytest

from mlca.api import Session
from mlca.errors import MlcaUserError
from mlca.project.init import column_for, study_ready


def test_deferred_resolution_preserves_answers_and_gates(project_factory):
    root = project_factory(brief={"aim": "inspect first", "target": "", "unit": ""})
    with Session.open(root) as session:
        assert session.state.columns["target"] is None
        session.confirm("brief_confirmed", "not resolved yet")
        with pytest.raises(MlcaUserError, match="incomplete"):
            session.next()
        session.resolve_study({"target": "y", "unit": "one sample"})
        assert column_for(session.state) == "y"
        assert study_ready(session.state)[0]
        assert session.state.original_brief["target"] == ""
        assert session.state.pending_options is None
        assert not session.state.confirmations
        assert session.state.generations["onboard"] == 2
        from mlca.evaluation.metrics import build

        assert build(session)["interventions"]["user"]["study_resolutions"]["value"] == 1
        with pytest.raises(MlcaUserError, match="Unresolved"):
            session.resolve_study({"target": "invented"})
        assert column_for(session.state) == "y"
    with Session.open(root) as session:
        assert session.state.columns["target"] == "y"
        assert session.state.original_brief["target"] == ""
        session.store.verify()
    with Session.open(root, principal="agent:test/1") as agent:
        with pytest.raises(MlcaUserError):
            agent.resolve_study({"target": "x1"})


def test_survival_deferred_columns(project_factory):
    root = project_factory(template="survival", brief={"aim": "survival", "target": "", "unit": ""})
    with Session.open(root) as session:
        session.resolve_study(
            {"duration": "duration", "target": "duration", "event_column": "observed", "unit": "patient"}
        )
        assert study_ready(session.state)[0]
        assert column_for(session.state, "event_column") == "observed"
