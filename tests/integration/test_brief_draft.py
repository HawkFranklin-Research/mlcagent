import json
from types import SimpleNamespace

from mlca.config import RoleConfig


def test_navigator_drafts_brief_from_column_summary_only(opened_project, monkeypatch):
    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    sent = []

    def complete(role, messages, **kwargs):
        sent.append((messages[-1]["content"], kwargs.get("categories")))
        draft = {
            "aim": "Predict y from x1–x4",
            "target": "y",
            "unit": "one simulated sample",
            "repeated": "No",
        }
        return SimpleNamespace(text=json.dumps(draft), request_id="fake")

    monkeypatch.setattr(s.client, "complete", complete)
    draft = s.draft_brief()
    assert draft["target"] == "y" and draft["unit"] == "one simulated sample"
    content, categories = sent[0]
    assert '"distinct"' in content and "x1" in content and "sample_rows" not in categories
    assert not any(r.type.value == "StudyFieldsResolved" for r in s.store.read()[-3:])


def test_draft_drops_invented_columns(opened_project, monkeypatch):
    s = opened_project
    s.config.roles["navigator"] = RoleConfig(provider="offline", model="scripted")
    monkeypatch.setattr(
        s.client,
        "complete",
        lambda *a, **kw: SimpleNamespace(
            text='{"aim": "a", "target": "salary", "unit": "u"}', request_id="f"
        ),
    )
    assert s.draft_brief()["target"] == ""
