import copy
from types import SimpleNamespace as NS

import pytest
from pydantic import BaseModel

from mlca.config import ProviderConfig, RoleConfig
from mlca.errors import MlcaUserError
from mlca.llm.client import RequestContext
from mlca.llm.usage import read


class Answer(BaseModel):
    text: str


class Failing(Exception):
    def __init__(self, status, headers=None):
        super().__init__(f"HTTP {status}")
        self.status_code = status
        self.response = NS(headers=headers or {})


def ok():
    return {
        "text": '{"text": "hi"}',
        "input_tokens": 5,
        "output_tokens": 2,
        "cached_tokens": 0,
        "cost_usd": 0.0,
    }


def setup(session, monkeypatch, responses):
    session.config.providers["router"] = ProviderConfig(
        kind="openrouter", structured_outputs=True, request_cost_bound_usd=0
    )
    session.config.roles["navigator"] = RoleConfig(provider="router", model="vendor/model:free")
    sent = []

    def complete(payload):
        sent.append(copy.deepcopy({k: v for k, v in payload.items() if k != "messages"}))
        item = responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(session.client, "_provider", lambda name: NS(complete=complete))
    sleeps = []
    monkeypatch.setattr("mlca.llm.client.time.sleep", sleeps.append)
    return sent, sleeps


def call(session):
    context = RequestContext(role="navigator", session_id=session.session_id, event_id="onboard", purpose="t")
    return session.client.complete(
        "navigator",
        [{"role": "user", "content": "x"}],
        schema=Answer,
        context=context,
        categories=["user_text"],
    )


def test_no_json_endpoint_retries_once_without_structured_output(opened_project, monkeypatch):
    sent, _ = setup(opened_project, monkeypatch, [Failing(404), ok(), ok()])
    call(opened_project)
    assert "response_format" in sent[0] and sent[0]["extra_body"]["provider"]["require_parameters"]
    assert "response_format" not in sent[1] and "provider" not in sent[1]["extra_body"]
    call(opened_project)  # remembered for the session: no second 404
    assert "response_format" not in sent[2]
    sources = [r["request_settings"]["structured_outputs_source"] for r in read(opened_project.root)]
    assert sources[-1] == "no_endpoint_fallback"


def test_rate_limits_wait_without_spending_attempts(opened_project, monkeypatch):
    errors = [Failing(429, {"retry-after": "7"}), Failing(429), Failing(429)]
    _, sleeps = setup(opened_project, monkeypatch, [*errors, ok()])
    call(opened_project)
    assert sleeps == [7.0, 15.0, 30.0]
    _, sleeps = setup(opened_project, monkeypatch, [Failing(429)] * 5)
    with pytest.raises(MlcaUserError) as raised:
        call(opened_project)
    assert raised.value.category == "provider_error" and len(sleeps) == 4
