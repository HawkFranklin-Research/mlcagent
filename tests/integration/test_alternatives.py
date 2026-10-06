import json

import pytest

from mlca.api import Session
from mlca.project.inventory import read_table
from tests.helpers import advance_to, choose_action


@pytest.mark.slow
def test_freeze_group_completes_split(project_factory, sandbox_level):
    with Session.open(project_factory(group=True)) as session:
        advance_to(session, "split")
        choose_action(session, "freeze_group", {"group_column": "group"})
        assert session.state.event_statuses["split"] == "done"
        assert session.next()["event"] == "preprocess"


@pytest.mark.slow
def test_alternative_only_completes_model(project_factory, sandbox_level):
    with Session.open(project_factory()) as session:
        advance_to(session, "model")
        choose_action(session, "train_alternative")
        assert session.state.event_statuses["model"] == "done"
        assert not any(s["action_id"] == "train_logistic" for s in session.state.steps)
        assert session.next()["event"] == "validate"


@pytest.mark.slow
def test_split_uses_structured_column(project_factory, sandbox_level):
    with Session.open(project_factory(brief={"aim": "test", "target": "Y", "unit": "row"})) as session:
        advance_to(session, "split")
        session.emit(
            "BriefRecorded",
            {"answers": {**session.state.brief, "target": "the wrong column"}, "columns": {"target": "y"}},
        )
        choose_action(session, "freeze_stratified")
        assert session.state.columns["target"] == "y"
        assert session.state.event_statuses["split"] == "done"
        onboard = session.state.steps[0]
        payload = json.loads((session.root / onboard["outputs"][0]["path"]).read_text())
        assert payload["columns"] == {"target": "y"}
        assert payload["brief"]["target"] == "Y"
        assert len(read_table(session.root / session.state.split["train"]["path"])) > 0
