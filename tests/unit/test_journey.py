from types import SimpleNamespace as NS

from mlca.tui.widgets.journey import strip, trail
from mlca.ui_text import record_message


def test_journey_plain_messages_and_branch_trail():
    status = {
        "current_event": "data",
        "event_statuses": {"onboard": "done"},
        "workflow": {"events": ["onboard", "data", "split"]},
    }
    assert strip(status) == "onboard ✓ → data ● → split 🔒"
    records = [
        NS(type=NS(value="StudyFieldsResolved"), payload={}),
        NS(type=NS(value="StepStarted"), payload={"action_id": "audit", "step_id": "s"}),
        NS(type=NS(value="StepCompleted"), payload={"step_id": "s"}),
    ]
    assert (
        trail(records, NS(actions={"audit": NS(title="Audit schema")}))
        == "Choose target (you) ✓ → Audit schema ✓"
    )
    record = NS(
        type=NS(value="InventoryRecorded"),
        payload={"files": [{"name": "table", "rows": 569, "columns": ["x", "y"]}]},
    )
    assert record_message(record) == "✓ Registered table table (569 rows, 2 columns)"
