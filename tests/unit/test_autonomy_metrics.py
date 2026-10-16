from types import SimpleNamespace as NS

from mlca.evaluation.autonomy import build
from mlca.evaluation.bench import autonomy_summary


def record(kind, payload=None, event="model"):
    return NS(type=NS(value=kind), payload=payload or {}, event_id=event)


def test_unknown_legacy_is_not_zero():
    result = build([], [])
    assert result["halts"] == {"value": None, "source": "unavailable"}
    assert result["inference"]["correctness"]["value"] is None
    summary = autonomy_summary([None], [{}])
    assert summary["halts"]["n"]["value"] == 0
    assert summary["runs_with_unavailable_metrics"]["value"] == 1


def test_derived_autonomy_and_actual_model_mix():
    rows = [
        record("ProjectCreated", {"rails": {"version": "rails-0.0", "sha256": "abc"}}),
        record("AutonomyConfigured", {"halt_window_s": 60}),
        record("InferenceRecorded", {"proposal": {"problem_type": "binary"}}),
        record("DecisionWindowHalted", {"wait_s": 4}),
        record("DecisionOverridden", {"selection": 1}),
        record("DecisionWindowExpired", {"wait_s": 60}, "data"),
        record("QuestionAutoResolved"),
        record("QuestionAsked"),
        record("RailFired", {"rail_id": "RL-0001"}),
    ]
    result = build(rows, [{"model_reported": "a"}, {"model_reported": "b"}, {"model_reported": "a"}, {}])
    assert result["halts"]["value"] == 1
    assert result["halts_by_event"]["model"]["value"] == 1
    assert result["window_wait_s"]["value"] == 64
    assert result["overrides"]["value"] == 1
    assert result["auto_resolved_questions"]["value"] == 1
    assert result["questions_asked"]["value"] == 1
    assert result["rails_fired"]["RL-0001"]["value"] == 1
    assert result["model_reported_distribution"]["a"]["value"] == 2
    assert result["model_reported_unavailable"]["value"] == 1
    summary = autonomy_summary([{"autonomy": result}, None], [{}, {"setup_usage": {"model_requests": 2}}])
    assert summary["model_reported_distribution"]["a"]["value"] == 2
    assert summary["setup_usage"][1]["model_requests"] == 2
