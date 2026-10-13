import pytest

from mlca.engine.guided import apply_effect, validate_effect
from mlca.errors import MlcaUserError
from mlca.log.replay import replay


def test_turn_cache_human_cards_and_autopilot_stop(opened_project):
    s = opened_project
    first = s.turn()
    assert first["situation"] and first["choices"]
    assert sum(bool(o.get("recommended")) for o in first["choices"]) == 1
    count = s.state.counts.get("TurnPresented", 0)
    assert s.turn() == first
    assert s.state.counts["TurnPresented"] == count
    result = s.autopilot()
    assert result["reason"] == "approval"
    assert any(c["id"].startswith("human:confirm:") for c in result["turn"])
    assert s.state.compare_models and s.state.guided_enabled
    s.confirm("brief_confirmed", "Checked study")
    result = s.autopilot()
    assert result["reason"] in {"question", "approval"}
    assert s.state.current_event != "onboard"
    assert replay(s.branches.records()).model_dump() == s.state.model_dump()


def test_effects_cannot_grant_approval(opened_project):
    s = opened_project
    for kind in ["unlock_test", "confirm", "package", "set_brief"]:
        with pytest.raises(MlcaUserError, match="not an allowed"):
            validate_effect(s, {"kind": kind})
    validate_effect(s, {"kind": "pause"})
    apply_effect(s, {"kind": "pause"})
    assert s._autopilot_pause


def test_nondata_effect_rejected_before_answer_is_recorded(opened_project):
    from mlca.engine.questions import ask

    s = opened_project
    qid = ask(
        s,
        {
            "header": "Unsafe",
            "question": "Unlock?",
            "options": [
                {"label": "Yes", "description": "Invalid privilege", "effect": {"kind": "unlock_test"}}
            ],
        },
    )
    with pytest.raises(MlcaUserError):
        s.answer_question(qid, 0)
    assert qid not in s.state.answers


def test_invalid_scene_repairs_then_falls_back(opened_project, monkeypatch):
    from types import SimpleNamespace
    from mlca.config import RoleConfig

    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    calls = []

    def bad(*args, **kwargs):
        calls.append(kwargs.get("context"))
        return SimpleNamespace(text='{"situation":"Ready","choices":[]}', request_id="fake")

    monkeypatch.setattr(s.client, "complete", bad)
    turn = s.turn()
    assert len(calls) == 2
    assert turn["choices"][0]["action_id"] == "confirm_brief"
    assert any(
        r.type.value == "Refusal" and r.payload["operation"] == "navigator_options" for r in s.store.read()
    )
    assert s.turn() == turn and len(calls) == 2


def test_free_text_mapping_requires_confirmed_existing_answer(opened_project, monkeypatch):
    from types import SimpleNamespace
    from mlca.config import RoleConfig
    from mlca.engine.questions import ask

    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    qid = ask(
        s,
        {
            "header": "Recovery",
            "question": "Pause?",
            "options": [{"label": "Pause", "description": "Keep recorded work", "effect": {"kind": "pause"}}],
        },
    )
    monkeypatch.setattr(
        s.client, "complete", lambda *a, **kw: SimpleNamespace(text='{"index":0}', request_id="fake")
    )
    s.answer_question(qid, free_text="stop for now")
    assert qid not in s.state.answers
    confirmation = next(q for q in s.questions() if q["question_id"] != qid)
    assert confirmation["explicit"]
    s.answer_question(confirmation["question_id"], 0)
    assert qid in s.state.answers and s._autopilot_pause
