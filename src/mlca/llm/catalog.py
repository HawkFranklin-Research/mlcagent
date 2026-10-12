"""Explicit model discovery; catalogue requests carry no study data."""

import hashlib
import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

import yaml

from mlca.errors import MlcaUserError
from mlca.paths import atomic_json, user_config_dir

from .credentials import resolve

DEFAULTS = {
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "openai_api": ("https://api.openai.com/v1", "OPENAI_API_KEY"),
    "openai_compatible": ("http://localhost:11434/v1", None),
}


@dataclass
class Model:
    id: str
    name: str
    input_per_million: float | None = None
    output_per_million: float | None = None
    context: int | None = None
    parameters: list[str] | None = None
    free: bool = False


def price(value):
    try:
        result = float(value)
        return result * 1_000_000 if math.isfinite(result) and result >= 0 else None
    except (ValueError, TypeError):
        return None


def parse(data: dict) -> list[Model]:
    result = []
    for entry in data.get("data", []):
        identifier = entry.get("id")
        if not isinstance(identifier, str) or not identifier:
            continue
        prices = entry.get("pricing") or {}
        a, b = price(prices.get("prompt")), price(prices.get("completion"))
        other = [price(v) for k, v in prices.items() if k not in {"prompt", "completion"}]
        if any(v != 0 for v in other):
            a, b = None, None  # Non-token/unknown fees need an explicit request bound.
        result.append(
            Model(
                identifier,
                entry.get("name") or identifier,
                a,
                b,
                entry.get("context_length"),
                entry.get("supported_parameters"),
                a == 0 and b == 0 and all(v == 0 for v in other),
            )
        )
    return sorted(result, key=lambda m: m.name.casefold())


def cache_path(provider):
    endpoint = provider.base_url or DEFAULTS.get(provider.kind, ("", None))[0]
    digest = hashlib.sha256((provider.kind + endpoint).encode()).hexdigest()[:24]
    return user_config_dir() / "catalog" / (digest + ".json")


def cached(provider) -> tuple[list[Model], bool]:
    try:
        data = json.loads(cache_path(provider).read_text())
        return parse(data["response"]), time.time() - data["fetched_at"] > 86400
    except (OSError, ValueError, KeyError):
        return [], True


def fetch(provider) -> list[Model]:
    base = provider.base_url or DEFAULTS.get(provider.kind, ("", None))[0]
    if not base or provider.kind == "fake":
        raise MlcaUserError("This provider has no model catalogue; enter a model ID manually")
    headers = {"Accept": "application/json"}
    key = resolve(provider.api_key_env)
    if key:
        headers["Authorization"] = "Bearer " + key
    request = urllib.request.Request(base.rstrip("/") + "/models", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = response.read(4 * 1024 * 1024 + 1)
        if len(body) > 4 * 1024 * 1024:
            raise ValueError("Catalogue exceeds size limit")
        from mlca.config import redact_value

        raw = redact_value(json.loads(body))
        data = {
            "data": [
                {
                    k: e[k]
                    for k in ["id", "name", "pricing", "context_length", "supported_parameters"]
                    if k in e
                }
                for e in raw.get("data", [])
                if isinstance(e, dict)
            ]
        }
        models = parse(data)
        if not models:
            raise ValueError("No models returned")
    except (OSError, ValueError, urllib.error.URLError):
        raise MlcaUserError(
            "Could not load models. Check credentials/endpoint, use cached models or enter an ID manually"
        ) from None
    atomic_json(cache_path(provider), {"fetched_at": time.time(), "response": data})
    return models


def save_prices(provider_name: str, models: list[Model]) -> None:
    path = user_config_dir() / "pricing.yaml"
    data = yaml.safe_load(path.read_text()) or {} if path.exists() else {}
    entries = data.setdefault(provider_name, {})
    for model in models:
        if model.input_per_million is not None and model.output_per_million is not None:
            entries[model.id] = {
                "input_per_million": model.input_per_million,
                "output_per_million": model.output_per_million,
                "source": "provider model catalogue",
                "fetched_at": time.time(),
            }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data))
    path.chmod(0o600)
