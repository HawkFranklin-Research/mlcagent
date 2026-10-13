from types import SimpleNamespace as NS

from mlca.engine.guidance import cards
from mlca.log.schema import ProjectState
from mlca.templates.registry import get


def test_human_cards_are_engine_generated_and_custom_last():
    state = ProjectState(current_event="onboard", columns={}, event_statuses={"onboard": "open"})
    session = NS(state=state, workflow=get("tabular_classification"), branches=NS(records=lambda: []))
    options = cards(session, [{"id": "custom", "title": "Custom"}])
    assert [o["id"] for o in options] == ["human:study", "locked:confirm_brief", "custom"]
    assert options[1]["disabled"] and "study details" in options[1]["description"]
    assert options[0]["source"] == "you decide"
    assert "exhausted" not in str(options).lower()
