import pandas as pd
import pytest

from mlca.engine.data_review import apply, findings
from mlca.errors import MlcaUserError
from mlca.log.replay import replay
from tests.helpers import choose_action


def test_generic_findings_and_effects():
    frame = pd.DataFrame(
        {
            "outcome": ["Yes.", " yes ", "No", "No", "Yes.", "No"] * 3,
            "patient_id": range(18),
            "source": [1, 1, 0, 0, 1, 0] * 3,
            "empty": [None] * 18,
            "value": range(18),
        }
    )
    qs = findings(frame, {"target": "outcome"}, "tabular_classification")
    keys = {q["key"] for q in qs}
    assert {"outcome_labels", "identifier:patient_id", "leakage:source", "missing:empty"} <= keys
    assert all(q["explicit"] for q in qs if q["key"] == "outcome_labels" or q["key"].startswith("leakage:"))
    decisions = [{"effect": q["options"][0]["effect"]} for q in qs]
    changed, excluded, group, _ = apply(frame, decisions)
    assert set(changed.outcome) == {"yes", "no"}
    assert "source" in excluded and "patient_id" in excluded
    assert len(frame) == 18 and frame.outcome.iloc[0] == "Yes."


def test_survival_alias_and_event_coding():
    frame = pd.DataFrame({"duration": range(1, 21), "event": [1, 2] * 10, "status": [1, 2] * 10})
    qs = findings(frame, {"target": "duration", "event_column": "event"}, "survival")
    assert {"leakage:status", "event_codes"} <= {q["key"] for q in qs}
    changed, _, _, _ = apply(frame, [{"effect": q["options"][0]["effect"]} for q in qs])
    assert set(changed.event) == {0, 1}


def test_review_replay_explicit_answers_and_gates(opened_project):
    from mlca.engine.questions import ask

    s = opened_project
    choose_action(s, "confirm_brief")
    s.confirm("brief_confirmed", "ready")
    s.next()
    s.review_data()
    # Re-open an explicit engine question under the same review context.
    qid = ask(
        s,
        {
            "header": "Possible outcome source",
            "question": "Exclude x1?",
            "options": [
                {
                    "label": "Exclude",
                    "description": "Exclude the column.",
                    "effect": {"kind": "exclude_column", "column": "x1"},
                },
                {"label": "Keep", "description": "Keep the column.", "effect": {"kind": "keep"}},
            ],
            "explicit": True,
            "human_only": True,
        },
        key="leakage:x1",
    )
    with pytest.raises(MlcaUserError, match="explicit"):
        s.answer_question(qid, default=True)
    with pytest.raises(MlcaUserError, match="pending"):
        s.choose("1")
    before = len(s.store.read())
    s.answer_question(qid, 0)
    rebuilt = replay(s.branches.records())
    assert rebuilt.data_decisions[-1]["effect"]["column"] == "x1"
    assert rebuilt.prepared_data and len(s.store.read()) > before
    assert s.questions() == []
    with pytest.raises(MlcaUserError):
        s.answer_question(qid, 0)


def test_group_and_duplicate_rules_are_properties_not_names():
    frame = pd.DataFrame(
        {
            "target": [0, 1, 0, 1] * 10,
            "subject_id": [i // 4 for i in range(40)],
            "x": [i % 4 for i in range(40)],
        }
    )
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    keys = {q["key"] for q in findings(frame, {"target": "target"}, "tabular_classification", "yes")}
    assert "group:subject_id" in keys and "duplicates" in keys


def test_multiple_outcomes_offer_an_explicit_choice():
    frame = pd.DataFrame({"result": [0, 1] * 20, "diagnosis": [0, 0, 1, 1] * 10, "x": range(40)})
    q = next(
        q
        for q in findings(frame, {"target": "result"}, "tabular_classification")
        if q["key"] == "outcome_choice"
    )
    assert q["explicit"] and q["options"][1]["effect"]["column"] == "diagnosis"
