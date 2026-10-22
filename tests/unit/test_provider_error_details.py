from types import SimpleNamespace as NS

import pytest

from mlca.config import ProviderConfig, RoleConfig
from mlca.errors import MlcaUserError
from mlca.llm.client import RequestContext
from mlca.llm.provider_errors import details
from mlca.llm.usage import read


def test_http400_keeps_only_bounded_redacted_provider_diagnostic(opened_project, monkeypatch):
    session = opened_project
    secret = "distinctive-offline-provider-key-8273"
    monkeypatch.setenv("DEEPSEEK_API_KEY", secret)
    session.config.providers["direct"] = ProviderConfig(kind="deepseek", request_cost_bound_usd=0)
    session.config.roles["worker"] = RoleConfig(provider="direct", model="offline")
    body = {
        "error": {"type": "invalid_request_error", "message": "Context exceeds limit " + secret + "x" * 600},
        "request": "PRIVATE_REQUEST_BODY",
    }
    error = MlcaUserError("HTTP 400")
    error.status_code = 400
    error.body = body
    error.response = NS(headers={"private": "PRIVATE_HEADER"})

    def fail(payload):
        raise error

    monkeypatch.setattr(session.client, "_provider", lambda _: NS(complete=fail))
    with pytest.raises(MlcaUserError):
        session.client.complete(
            "worker",
            [{"role": "user", "content": "PRIVATE_REQUEST_BODY"}],
            context=RequestContext(role="worker", session_id=session.session_id),
            categories=[],
        )
    record = read(session.root)[-1]
    assert record["status_code"] == 400
    assert record["provider_error_type"] == "invalid_request_error"
    assert record["provider_error_message"].startswith("Context exceeds limit [REDACTED]")
    assert len(record["provider_error_message"]) == 500
    event = next(r for r in reversed(session.store.read()) if r.type.value == "ProviderFailed")
    assert event.payload["provider_error_message"] == record["provider_error_message"]
    for item in (record, event.payload):
        assert (
            secret not in str(item)
            and "PRIVATE_HEADER" not in str(item)
            and "PRIVATE_REQUEST_BODY" not in str(item)
        )


def test_deadline_transport_keeps_error_fields(monkeypatch):
    from mlca.llm.providers.deepseek import DeepSeekProvider

    monkeypatch.setenv("DEEPSEEK_API_KEY", "offline-only")
    provider = DeepSeekProvider(ProviderConfig(kind="deepseek", call_deadline_s=3))
    monkeypatch.setattr(
        "mlca.llm.deadline.exchange",
        lambda *_: {
            "error": "HTTP 400",
            "status_code": 400,
            "provider_error_type": "invalid_request_error",
            "provider_error_message": "Too many input tokens",
        },
    )
    with pytest.raises(MlcaUserError) as caught:
        provider.complete({})
    assert details(caught.value) == {
        "provider_error_type": "invalid_request_error",
        "provider_error_message": "Too many input tokens",
    }
    assert details(ValueError("private local error")) == {}
