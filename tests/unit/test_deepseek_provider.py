"""Offline direct-provider contracts; no network or real credentials."""

from types import SimpleNamespace as NS

import pytest
from pydantic import BaseModel

from mlca.config import ProviderConfig, RoleConfig
from mlca.errors import MlcaUserError
from mlca.llm import usage
from mlca.llm.client import RequestContext
from mlca.llm.providers.deepseek import DeepSeekProvider
from mlca.tui.screens.onboarding import KINDS


def test_defaults_and_dispatch(opened_project, monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "offline-test-key")
    cfg = ProviderConfig(kind="deepseek")
    assert cfg.base_url == "https://api.deepseek.com"
    assert cfg.api_key_env == "DEEPSEEK_API_KEY"
    opened_project.config.providers["direct"] = cfg
    provider = opened_project.client._provider("direct")
    assert isinstance(provider, DeepSeekProvider)
    assert str(provider.client.base_url) == "https://api.deepseek.com"
    assert ("DeepSeek (direct API)", "deepseek") in KINDS


def test_missing_key_is_refused(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    with pytest.raises(MlcaUserError, match="Missing environment variable: DEEPSEEK_API_KEY"):
        DeepSeekProvider(ProviderConfig(kind="deepseek"))


class Answer(BaseModel):
    ok: bool


@pytest.mark.parametrize("structured", [False, True])
@pytest.mark.parametrize("effort", [None, "low", "none", "high"])
def test_request_and_accounting(opened_project, monkeypatch, structured, effort):
    s = opened_project
    s.config.providers["direct"] = ProviderConfig(
        kind="deepseek", structured_outputs=structured, request_cost_bound_usd=0.1
    )
    s.config.roles["worker"] = RoleConfig(provider="direct", model="deepseek-flash", reasoning_effort=effort)
    payloads = []

    def complete(payload):
        payloads.append(payload)
        return {
            "text": '{"ok":true}',
            "input_tokens": 10,
            "output_tokens": 5,
            "cached_tokens": 3,
            "model_reported": "server-returned-model",
            "provider_request_id": "direct-request",
            "cost_usd": None,
        }

    monkeypatch.setattr(s.client, "_provider", lambda _: NS(complete=complete))
    messages = [{"role": "user", "content": "Return JSON"}]
    s.client.complete(
        "worker",
        messages,
        schema=Answer,
        context=RequestContext(role="worker", session_id=s.session_id),
        categories=[],
    )
    payload = payloads[0]
    assert payload["model"] == "deepseek-flash"
    assert payload["max_tokens"] == 16384
    assert "max_completion_tokens" not in payload
    assert "extra_body" not in payload  # No OpenRouter routing or user identifiers.
    assert payload.get("reasoning_effort") == effort
    if effort is None:
        assert "reasoning_effort" not in payload
    if structured:
        assert payload["response_format"] == {"type": "json_object"}
        assert "schema" in payload["messages"][-1]["content"]
    else:
        assert "response_format" not in payload
    assert len(messages) == 1
    record = usage.read(s.root)[-1]
    assert record["provider_kind"] == "deepseek"
    assert record["model_reported"] == "server-returned-model"
    assert record["cost_usd"] is None
    assert record["cost_source"] == "unknown"


def test_direct_cache_usage(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "offline-test-key")
    provider = DeepSeekProvider(ProviderConfig(kind="deepseek"))
    body = {
        "choices": [{"message": {"content": "{}"}, "finish_reason": "stop"}],
        "model": "returned-model",
        "id": "direct-id",
        "usage": {"prompt_tokens": 10, "completion_tokens": 4, "prompt_cache_hit_tokens": 7},
    }
    provider.client = NS(chat=NS(completions=NS(create=lambda **_: NS(model_dump=lambda: body))))
    result = provider.complete({})
    assert result["cached_tokens"] == 7
    assert result["cost_usd"] is None
    assert result["model_reported"] == "returned-model"
