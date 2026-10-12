"""Explicit provider quota metadata; unknown schemas/values never become zeros."""

import hashlib
import json
import time
import urllib.request

from mlca.errors import MlcaUserError
from mlca.paths import atomic_json

from .credentials import resolve


def refresh(root, config):
    snapshots = {}
    for name, provider in config.providers.items():
        if provider.kind != "openrouter":
            continue
        key = resolve(provider.api_key_env)
        if not key:
            continue
        try:
            request = urllib.request.Request(
                "https://openrouter.ai/api/v1/key", headers={"Authorization": "Bearer " + key}
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                data = json.loads(response.read(65536)).get("data", {})
            daily = data.get("free_model_daily_requests")
            used = limit = None
            if isinstance(daily, dict):
                used = daily.get("used", daily.get("count"))
                limit = daily.get("limit")

            def number(value):
                return (
                    value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None
                )

            snapshots[name] = {
                "used": number(used),
                "limit": number(limit),
                "fetched_at": time.time(),
                "source": "OpenRouter /key",
                "credential_sha256": hashlib.sha256(key.encode()).hexdigest(),
            }
        except Exception:
            raise MlcaUserError(
                "Could not refresh OpenRouter quota; existing request counts are project-local only"
            ) from None
    if not (root / ".mlca/project.yaml").exists():
        raise MlcaUserError("Open a project before recording quota metadata")
    atomic_json(root / ".mlca/provider-quota.json", snapshots)
    return snapshots


def cached(root):
    path = root / ".mlca/provider-quota.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {}


def for_provider(root, name, provider):
    key = resolve(provider.api_key_env)
    value = cached(root).get(name, {})
    if key and value.get("credential_sha256") == hashlib.sha256(key.encode()).hexdigest():
        return value
    return {}
