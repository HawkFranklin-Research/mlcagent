from types import SimpleNamespace as NS

import pytest

from mlca.config import RoleConfig
from mlca.errors import BudgetError, IntegrityError, MlcaUserError
from mlca.llm.usage import read
from mlca.roles.navigator import Navigator
from mlca.ui_text import record_message


@pytest.mark.parametrize(
    "error", [MlcaUserError("offline"), RuntimeError("response failed"), BudgetError("limit")]
)
def test_navigator_failure_leaves_template_choices_available(opened_project, monkeypatch, error):
    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    monkeypatch.setattr(Navigator, "propose_options", lambda *_: (_ for _ in ()).throw(error))
    choices = s.options()
    assert any(c.get("action_id") == "confirm_brief" for c in choices)
    record = next(r for r in s.store.read() if r.type.value == "OptionsProposed")
    assert record.payload["source"] == "fallback"
    refusal = next(r for r in s.store.read() if r.type.value == "Refusal")
    assert "built-in cards" in record_message(refusal)
    assert not s.state.steps and not read(s.root)


def test_navigator_does_not_hide_integrity_errors(opened_project, monkeypatch):
    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    monkeypatch.setattr(
        Navigator, "propose_options", lambda *_: (_ for _ in ()).throw(IntegrityError("tampered"))
    )
    with pytest.raises(IntegrityError):
        s.options()


def test_invalid_answer_has_one_repair_and_caches_template_options(opened_project, monkeypatch):
    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    calls = []

    def complete(*args, **kwargs):
        calls.append(kwargs)
        return NS(text="not JSON", request_id="scripted")

    monkeypatch.setattr(s.client, "complete", complete)
    first = s.options()
    assert len(calls) == 2
    assert s.options() == first and len(calls) == 2
