"""Explicit, metadata-only OpenRouter accounting repair; never invokes a model."""

import json
import math
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from mlca.config import redact_value
from mlca.errors import MlcaUserError
from mlca.llm.credentials import resolve
from mlca.llm.usage import fill_missing, read

ENDPOINT = "https://openrouter.ai/api/v1"


def fetch_generation(provider, identifier):
    if provider.base_url not in {None, ENDPOINT}:
        raise MlcaUserError("Backfill requires the official OpenRouter endpoint")
    key = resolve(provider.api_key_env)
    if not key:
        raise MlcaUserError("OpenRouter credential unavailable")
    request = urllib.request.Request(
        ENDPOINT + "/generation?" + urllib.parse.urlencode({"id": identifier}),
        headers={"Authorization": "Bearer " + key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=provider.timeout_s) as response:
        body = response.read(1024 * 1024 + 1)
    if len(body) > 1024 * 1024:
        raise MlcaUserError("Generation metadata exceeds the size limit")
    data = json.loads(body)["data"]
    if data.get("id") != identifier:
        raise MlcaUserError("Generation metadata does not match the requested ID")
    return data


def generation_values(data):
    mapping = {
        "input_tokens": "native_tokens_prompt",
        "output_tokens": "native_tokens_completion",
        "reasoning_tokens": "native_tokens_reasoning",
        "cached_tokens": "native_tokens_cached",
        "cache_write_tokens": "native_tokens_cache_write",
        "cost_usd": "total_cost",
        "upstream_cost_usd": "upstream_inference_cost",
        "provider_reported": "provider_name",
        "model_reported": "model",
    }
    values = {field: data.get(source) for field, source in mapping.items()}
    for field in mapping:
        value = values[field]
        if field.endswith("tokens") or field.endswith("cost_usd"):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                values[field] = None
    # The generation endpoint only reports upstream costs meaningfully for BYOK.
    if not data.get("is_byok"):
        values["upstream_cost_usd"] = None
    return values


def backfill(session, *, fetch=fetch_generation, sleep=time.sleep, clock=time.monotonic, now=None):
    now = now or datetime.now(timezone.utc)
    report = {"updated": [], "unrecoverable": [], "skipped": [], "failed": []}
    last = None
    for record in read(session.root):
        provider = session.config.providers.get(record.get("provider"))
        kind = record.get("provider_kind") or (provider.kind if provider else None)
        if kind != "openrouter" or record.get("cost_usd") is not None:
            continue
        identifier = record.get("provider_request_id")
        item = {"request_id": record["request_id"]}
        if not identifier:
            report["unrecoverable"].append({**item, "reason": "no_generation_id"})
            continue
        try:
            timestamp = datetime.fromisoformat(record["ts"].replace("Z", "+00:00"))
            if timestamp.tzinfo is None or timestamp < now - timedelta(days=30) or timestamp > now:
                report["skipped"].append({**item, "reason": "outside_30_day_window"})
                continue
        except (ValueError, KeyError):
            report["skipped"].append({**item, "reason": "invalid_timestamp"})
            continue
        if not provider or provider.kind != "openrouter":
            report["skipped"].append({**item, "reason": "provider_config_unavailable"})
            continue
        if last is not None:
            sleep(max(0, 1 - (clock() - last)))
        last = clock()
        try:
            data = fetch(provider, identifier)
            if data.get("id") != identifier:
                raise MlcaUserError("Generation metadata does not match the requested ID")
            values = redact_value(generation_values(data), session.config)
            changed = fill_missing(session.root, record["request_id"], values)
            report["updated"].append({**item, "fields": changed})
        except Exception as exc:
            # Never echo network errors, URLs or credentials into the report.
            report["failed"].append({**item, "error_type": type(exc).__name__})
    return report
