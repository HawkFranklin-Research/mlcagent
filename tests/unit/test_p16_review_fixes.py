from types import SimpleNamespace as NS

from mlca.config import ProviderConfig
from mlca.evaluation.metrics import navigator_use
from mlca.llm import usage
from mlca.llm.client import structured_setting


def test_optional_usage_fields_do_not_make_totals_partial():
    # A normal response: no cache-write field (no explicit caching), no upstream cost (not BYOK).
    record = {
        "role": "worker",
        "input_tokens": 1200,
        "output_tokens": 300,
        "reasoning_tokens": 0,
        "cached_tokens": 0,
        "cache_write_tokens": None,
        "upstream_cost_usd": None,
        "cost_usd": 0.0,
        "latency_ms": 900,
        "cost_source": "provider",
    }
    totals = usage.summary([record, {**record}])["totals"]
    assert totals["partial"] is False and totals["input_tokens"] == 2400
    cache_write = usage.measured_total(totals, "cache_write_tokens")
    assert cache_write["unreported_requests"] == 2 and cache_write["reported_requests"] == 0
    assert usage.summary([{**record, "output_tokens": None}])["totals"]["partial"] is True


def rec(kind, **payload):
    return NS(type=NS(value=kind), payload=payload)


def test_navigator_fallbacks_and_budget_stops_are_counted_separately():
    records = [
        rec("OptionsProposed", source="navigator"),
        rec("OptionsProposed", source="navigator"),
        rec("Refusal", operation="navigator_options", category="invalid_options"),
        rec("OptionsProposed", source="fallback"),
        rec("Refusal", operation="navigator_options", category="budget_stop"),
        rec("Refusal", operation="session", category="gate_blocked"),
    ]
    use = navigator_use(records)
    assert use["proposals_used"]["value"] == 2 and use["fallbacks"]["value"] == 1
    assert use["budget_stops"]["value"] == 1
    assert abs(use["fallback_rate"]["value"] - 1 / 3) < 1e-9
    assert navigator_use([])["fallback_rate"]["value"] is None


def test_structured_output_setting_states_its_source(monkeypatch):
    explicit = ProviderConfig(kind="openrouter", structured_outputs=False)
    assert structured_setting(explicit, "a/b") == (False, "config")
    assert structured_setting(ProviderConfig(kind="openai_compatible"), "m") == (False, "default")
    monkeypatch.setattr("mlca.llm.catalog.cached", lambda provider: ([], True))
    assert structured_setting(ProviderConfig(kind="openrouter"), "a/b") == (False, "no_catalogue")
    model = NS(id="a/b", json_output=True)
    monkeypatch.setattr("mlca.llm.catalog.cached", lambda provider: ([model], False))
    assert structured_setting(ProviderConfig(kind="openrouter"), "a/b") == (True, "catalogue")
