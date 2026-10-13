from types import SimpleNamespace as NS

import pandas as pd

from mlca.engine.suggest import recommendations
from mlca.tui.widgets.journey import flow
from mlca.ui_text import next_hint, record_message, scope_message


def rec(kind, payload):
    return NS(type=NS(value=kind), payload=payload)


def test_flow_is_plain_left_to_right_and_collapses_repeats():
    records = [
        rec("InventoryRecorded", {"files": [{"name": "table", "rows": 569, "columns": ["x", "y"]}]}),
        rec("BriefRecorded", {}),
        rec("StudyFieldsResolved", {}),
        rec("StudyFieldsResolved", {}),
        rec("EventEntered", {"event_id": "onboard", "via": "study_fields_updated"}),
    ]
    assert flow(records) == [
        "✓ Registered table table (569 rows, 2 columns)",
        "✓ Brief recorded",
        "✓ Study details chosen by you",
        "↻ Setup re-checked after your study details",
    ]


def test_scope_decisions_are_shown_in_plain_words():
    assert scope_message({"decision": "in_scope", "layer": 1}) is None
    moved = scope_message(
        {"decision": "other_event", "target_event": "model", "reason": "training belongs later"}
    )
    assert moved.startswith("⚠ Your instruction belongs to model") and "training belongs later" in moved
    assert scope_message({"decision": "reject", "layer": 1, "reason": "Test partition is locked"}) == (
        "⚠ Instruction not run: Test partition is locked"
    )
    approved = rec("ApprovalResolved", {"decision": "approved", "kind": "study_fields"})
    assert record_message(approved) == "✓ You approved: study fields"


def test_next_hint_names_the_missing_field_and_model():
    event = {
        "id": "onboard",
        "title": "Project setup",
        "subgoals": [
            {"id": "study_fields", "text": "Main table…", "check": {"type": "study_fields_resolved"}}
        ],
    }
    status = {
        "event_spec": event,
        "subgoals": {"onboard.study_fields": {"passed": False, "detail": "Explain what one row represents"}},
        "workflow": {"events": ["onboard", "data"]},
        "model_status": {"navigator": {}},
    }
    assert "what one row represents" in next_hint(status)
    assert next_hint({**status, "model_status": {}}).startswith("connect an AI model")


def test_rules_recommend_the_outcome_column():
    frame = pd.DataFrame(
        {
            "id": range(100),
            "Area": [float(i) * 1.37 for i in range(100)],
            "Class": ["A", "B", "C", "D"] * 25,
        }
    )
    ranked = recommendations(frame, "tabular_classification")["target"]
    assert ranked[0][0] == "Class"
    survival = pd.DataFrame({"time": [float(i) for i in range(50)], "cens": [0, 1] * 25, "age": [40] * 50})
    picks = recommendations(survival, "survival")
    assert picks["duration"][0][0] == "time" and picks["event_column"][0][0] == "cens"
