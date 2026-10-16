import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace as NS

import pytest
import yaml
from openai.types.chat import ChatCompletion
from pydantic import BaseModel
from typer.testing import CliRunner

from mlca.cli.main import app
from mlca.config import ProviderConfig, RoleConfig
from mlca.llm import usage
from mlca.llm.backfill import backfill
from mlca.llm.client import RequestContext
from mlca.llm.providers.openai_compatible import CompatibleProvider

BODY = {
    "id": "gen-test",
    "object": "chat.completion",
    "created": 1,
    "model": "actual-model",
    "provider": "actual-provider",
    "choices": [{"index": 0, "finish_reason": "stop", "message": {"role": "assistant", "content": "{}"}}],
    "usage": {
        "prompt_tokens": 12,
        "completion_tokens": 8,
        "total_tokens": 20,
        "completion_tokens_details": {"reasoning_tokens": 3},
        "prompt_tokens_details": {"cached_tokens": 4, "cache_write_tokens": 2},
        "cost": 0,
        "cost_details": {"upstream_inference_cost": 0.002},
    },
}


def adapter_result(body):
    adapter = object.__new__(CompatibleProvider)
    adapter.client = NS(chat=NS(completions=NS(create=lambda **kwargs: ChatCompletion.model_validate(body))))
    return adapter.complete({})


def test_sdk_preserves_extended_usage_and_unknown_fields():
    result = adapter_result(BODY)
    assert result["reasoning_tokens"] == 3
    assert result["cache_write_tokens"] == 2
    assert result["upstream_cost_usd"] == 0.002
    assert result["provider_reported"] == "actual-provider"
    assert result["provider_request_id"] == "gen-test"
    unknown = adapter_result({**BODY, "usage": None, "provider": None})
    for field in ("reasoning_tokens", "cache_write_tokens", "upstream_cost_usd", "provider_reported"):
        assert unknown[field] is None


class Response(BaseModel):
    ok: bool


def call(session):
    return session.client.complete(
        "worker",
        [],
        schema=Response,
        context=RequestContext(role="worker", session_id=session.session_id),
        categories=[],
    )


@pytest.mark.parametrize("kind", ["openrouter", "openai_api", "openai_compatible", "fake"])
@pytest.mark.parametrize("structured", [None, True, False])
def test_record_settings_and_optional_fields(opened_project, monkeypatch, kind, structured):
    s = opened_project
    s.config.providers["offline"] = ProviderConfig(
        kind=kind,
        structured_outputs=structured,
        request_cost_bound_usd=0,
    )
    s.config.roles["worker"] = RoleConfig(provider="offline", model="selected")
    s.config.privacy.provider_data_collection = "deny"
    s.config.privacy.zero_data_retention = True
    monkeypatch.setattr("mlca.llm.catalog.cached", lambda *_: ([NS(id="selected", json_output=True)], False))
    payloads = []

    def complete(payload):
        payloads.append(payload)
        return adapter_result(BODY)

    monkeypatch.setattr(s.client, "_provider", lambda *_: NS(complete=complete))
    call(s)
    payload = payloads[0]
    record = usage.read(s.root)[0]
    assert record["reasoning_tokens"] == 3 and record["output_tokens"] == 8
    assert record["provider_request_id"] == "gen-test"
    assert record["provider_reported"] == "actual-provider"
    expected = structured is True or kind == "openrouter" and structured is None
    assert ("response_format" in payload) == expected
    if kind == "openrouter":
        project = yaml.safe_load((s.root / ".mlca/project.yaml").read_text())
        identifier = "mlca-" + hashlib.sha256(project["project_id"].encode()).hexdigest()[:16]
        assert record["end_user"] == payload["extra_body"]["user"] == identifier
        routing = payload["extra_body"]["provider"]
        assert routing == {
            "data_collection": "deny",
            "zdr": True,
            **({"require_parameters": True} if expected else {}),
        }
        assert "models" not in payload["extra_body"] and "allow_fallbacks" not in routing
        assert record["request_settings"]["extra_body"] == payload["extra_body"]
    else:
        assert "extra_body" not in payload and record["end_user"] is None


def test_pseudonym_stability_and_project_separation(project_factory, monkeypatch):
    from mlca.api import Session

    values = []
    for root in (project_factory(), project_factory()):
        with Session.open(root) as s:
            s.config.providers["offline"] = ProviderConfig(kind="openrouter", request_cost_bound_usd=0)
            monkeypatch.setattr(
                s.client, "_provider", lambda *_: NS(complete=lambda payload: adapter_result(BODY))
            )
            call(s)
            call(s)
            users = [r["end_user"] for r in usage.read(root)]
            assert len(set(users)) == 1
            values.append(users[0])
    assert values[0] != values[1]


def test_partial_totals_and_model_axis():
    rows = [
        {
            "role": "worker",
            "model_reported": "m",
            "input_tokens": 10,
            "output_tokens": 8,
            "reasoning_tokens": 3,
            "cache_write_tokens": 2,
            "cost_usd": 0,
            "latency_ms": 1,
        },
        {"role": "worker", "model_reported": "m", "input_tokens": None, "cost_usd": None},
    ]
    summary = usage.summary(rows)
    total = summary["totals"]
    assert total["input_tokens"] == 10 and total["unknown_input_tokens_requests"] == 1
    assert total["reasoning_tokens"] == 3 and total["output_tokens"] == 8
    assert total["cached_tokens"] is None and total["partial"]
    assert summary["groups"]["model_reported"]["m"] == total
    assert usage.summary([])["totals"]["input_tokens"] == 0
    assert usage.measured_total(total, "input_tokens")["value"] is None
    assert usage.measured_total(total, "input_tokens")["known_value"] == 10


def test_fake_records_and_cli_csv(opened_project, tmp_path):
    s = opened_project
    s.client._provider("offline").responses.insert(0, {"match": {}, "text": "{}"})
    call(s)
    record = usage.read(s.root)[0]
    assert record["reasoning_tokens"] is None and record["provider_request_id"] is None
    destination = tmp_path / "usage.csv"
    result = CliRunner().invoke(app, ["-p", str(s.root), "usage", "--csv", str(destination), "--json"])
    assert result.exit_code == 0, result.output
    rows = list(csv.DictReader(destination.open()))
    assert len(rows) == 1
    assert rows[0]["project_id"] == s.state.project_id
    assert "request_settings" in rows[0] and "payload" not in rows[0]
    assert json.loads(result.output)["totals"]["reasoning_tokens"] is None


def envelope(s, identifier, **fields):
    record = {
        "request_id": identifier,
        "provider": "router",
        "provider_kind": "openrouter",
        "role": "worker",
        "ts": datetime.now(timezone.utc).isoformat(),
        "cost_usd": None,
        "cost_source": "unknown",
        **fields,
    }
    usage.persist(s.root, record, {"request_id": identifier, "hash": "original"})


def test_backfill_missing_only_throttle_and_unrecoverable(opened_project):
    s = opened_project
    s.config.providers["router"] = ProviderConfig(kind="openrouter")
    envelope(s, "a", provider_request_id="gen-a", input_tokens=999)
    envelope(s, "b", provider_request_id="gen-b")
    envelope(s, "c")
    envelope(
        s, "d", provider_request_id="gen-d", ts=(datetime.now(timezone.utc) - timedelta(days=31)).isoformat()
    )
    envelope(s, "e", provider_request_id="gen-e", cost_usd=0)
    waits, calls = [], []

    def fetch(_, identifier):
        calls.append(identifier)
        return {
            "id": identifier,
            "total_cost": 0.02,
            "native_tokens_prompt": 4,
            "native_tokens_completion": 5,
            "native_tokens_reasoning": 2,
            "model": "actual",
            "provider_name": "provider",
        }

    report = backfill(s, fetch=fetch, sleep=waits.append, clock=lambda: 0)
    assert calls == ["gen-a", "gen-b"] and waits == [1]
    assert report["unrecoverable"][0]["request_id"] == "c"
    assert report["skipped"][0]["request_id"] == "d"
    records = {r["request_id"]: r for r in usage.read(s.root)}
    assert records["a"]["input_tokens"] == 999 and records["a"]["cost_source"] == "generation_endpoint"
    assert records["b"]["reasoning_tokens"] == 2 and records["b"].get("cache_write_tokens") is None
    assert json.loads((s.root / ".mlca/requests/a.json").read_text())["egress"]["hash"] == "original"
    before = (s.root / ".mlca/requests/a.json").read_bytes()
    backfill(s, fetch=lambda *_: pytest.fail("Unexpected fetch"))
    assert (s.root / ".mlca/requests/a.json").read_bytes() == before


def test_backfill_identity_failure_is_safe(opened_project):
    s = opened_project
    s.config.providers["router"] = ProviderConfig(kind="openrouter")
    envelope(s, "a", provider_request_id="gen-a")
    result = backfill(s, fetch=lambda *_: {"id": "gen-other"})
    assert result["failed"] == [{"request_id": "a", "error_type": "MlcaUserError"}]
    assert usage.read(s.root)[0]["cost_usd"] is None


def test_no_catalogue_or_privacy_does_not_force_settings(opened_project, monkeypatch):
    s = opened_project
    s.config.providers["offline"] = ProviderConfig(kind="openrouter", request_cost_bound_usd=0)
    monkeypatch.setattr("mlca.llm.catalog.cached", lambda *_: ([], True))
    sent = []
    monkeypatch.setattr(
        s.client,
        "_provider",
        lambda *_: NS(complete=lambda payload: sent.append(payload) or adapter_result(BODY)),
    )
    call(s)
    assert set(sent[0]["extra_body"]) == {"user"}
    assert "response_format" not in sent[0]


def test_provider_refusal_preserves_accounting(opened_project, monkeypatch):
    from mlca.errors import MlcaUserError

    s = opened_project
    refused = {
        **BODY,
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": None, "refusal": "no"},
            }
        ],
    }
    monkeypatch.setattr(
        s.client, "_provider", lambda *_: NS(complete=lambda payload: adapter_result(refused))
    )
    with pytest.raises(MlcaUserError):
        call(s)
    row = usage.read(s.root)[0]
    assert row["status"] == "error" and row["provider_request_id"] == "gen-test"
    assert row["cost_usd"] == 0 and row["reasoning_tokens"] == 3


def test_backfill_known_cost_is_read_only(opened_project):
    s = opened_project
    s.config.providers["router"] = ProviderConfig(kind="openrouter")
    envelope(s, "a", provider_request_id="gen-a", cost_usd=0)
    before = {p: p.read_bytes() for p in (s.root / ".mlca").rglob("*") if p.is_file()}
    assert backfill(s, fetch=lambda *_: pytest.fail("Network called"))["updated"] == []
    assert all(p.read_bytes() == content for p, content in before.items())


def test_reported_provider_is_redacted(opened_project, monkeypatch):
    s = opened_project
    monkeypatch.setenv("P16_KEY", "p16-credential-canary")
    s.config.providers["offline"].api_key_env = "P16_KEY"
    result = {**adapter_result(BODY), "provider_reported": "p16-credential-canary"}
    monkeypatch.setattr(s.client, "_provider", lambda *_: NS(complete=lambda payload: result))
    call(s)
    assert usage.read(s.root)[0]["provider_reported"] == "[REDACTED]"
    assert "p16-credential-canary" not in (s.root / ".mlca/usage.jsonl").read_text()


def test_status_bar_accepts_unavailable_cost(monkeypatch):
    from mlca.tui.widgets.status_bar import StatusBar

    widget = StatusBar()
    captured = []
    monkeypatch.setattr(widget, "update", captured.append)
    widget.render_state(
        {
            "branch": "main",
            "current_event": "data",
            "usage": {"model_requests": 1, "known_cost_usd": None, "unknown_cost_requests": 1},
        }
    )
    assert "unavailable" in captured[0].plain


def test_generation_http_is_metadata_only_and_validated(monkeypatch):
    import io

    from mlca.llm.backfill import fetch_generation

    monkeypatch.setenv("P16_KEY", "p16-http-canary")
    requests = []

    def opened(request, timeout):
        requests.append(request)
        return io.BytesIO(b'{"data":{"id":"gen-one","total_cost":0}}')

    monkeypatch.setattr("mlca.llm.backfill.urllib.request.urlopen", opened)
    provider = ProviderConfig(kind="openrouter", api_key_env="P16_KEY")
    assert fetch_generation(provider, "gen-one")["total_cost"] == 0
    assert requests[0].full_url == "https://openrouter.ai/api/v1/generation?id=gen-one"
    assert requests[0].get_header("Authorization") == "Bearer p16-http-canary"
    provider.base_url = "https://example.org"
    from mlca.errors import MlcaUserError

    with pytest.raises(MlcaUserError, match="official"):
        fetch_generation(provider, "gen-one")
    assert len(requests) == 1


@pytest.mark.parametrize("effort", [None, "low", "medium"])
def test_reasoning_effort_is_explicit_preserved_and_unset_by_default(opened_project, monkeypatch, effort):
    s = opened_project
    s.config.providers["offline"] = ProviderConfig(kind="openrouter", request_cost_bound_usd=0)
    s.config.roles["worker"] = RoleConfig(provider="offline", model="selected", reasoning_effort=effort)
    payloads = []

    def complete(payload):
        payloads.append(payload)
        return adapter_result(BODY)

    monkeypatch.setattr(s.client, "_provider", lambda *_: NS(complete=complete))
    call(s)
    extra = payloads[0]["extra_body"]
    assert extra["user"].startswith("mlca-")
    assert extra.get("reasoning") == (None if effort is None else {"effort": effort})
    assert usage.read(s.root)[0]["request_settings"]["reasoning_effort"] == effort
