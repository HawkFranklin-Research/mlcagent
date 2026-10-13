"""Explicit model discovery; catalogue requests carry no study data."""

import csv
import datetime
import hashlib
import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import yaml

from mlca.errors import MlcaUserError
from mlca.paths import atomic_json, user_config_dir

from .credentials import resolve

DEFAULTS = {
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    "openai_chatgpt": ("https://api.openai.com/v1", None),
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
    text_output: bool | None = None  # None: the provider did not say
    text_only: bool | None = None  # text is the only output (excludes e.g. music models)
    router: bool = False  # picks a different model per request, e.g. openrouter/free
    coding_index: float | None = None  # third-party Artificial Analysis score, when listed
    agentic_index: float | None = None

    @property
    def json_output(self) -> bool:
        return bool({"response_format", "structured_outputs"} & set(self.parameters or []))


def price(value):
    try:
        result = float(value)
        return result * 1_000_000 if math.isfinite(result) and result >= 0 else None
    except (ValueError, TypeError):
        return None


def parse(data: dict) -> list[Model]:
    if "models" in data:
        data = {
            "data": [
                {"id": m["slug"], "name": m.get("display_name", m["slug"])}
                for m in data["models"]
                if m.get("visibility") == "list" and m.get("slug")
            ]
        }
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
        architecture = entry.get("architecture") or {}
        outputs = architecture.get("output_modalities")
        index = (entry.get("benchmarks") or {}).get("artificial_analysis") or {}
        result.append(
            Model(
                identifier,
                entry.get("name") or identifier,
                a,
                b,
                entry.get("context_length"),
                entry.get("supported_parameters"),
                a == 0 and b == 0 and all(v == 0 for v in other),
                ("text" in outputs) if isinstance(outputs, list) and outputs else None,
                (outputs == ["text"]) if isinstance(outputs, list) and outputs else None,
                architecture.get("tokenizer") == "Router",
                index.get("coding_index") if isinstance(index.get("coding_index"), (int, float)) else None,
                index.get("agentic_index") if isinstance(index.get("agentic_index"), (int, float)) else None,
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
    if provider.kind == "openai_chatgpt":
        from .openai_auth import RESOURCE, access_token, reference

        if (
            base != RESOURCE
            or not provider.oauth_client_id
            or provider.api_key_env != reference(provider.oauth_client_id)
        ):
            raise MlcaUserError("ChatGPT catalogue requires MLCA registration and the public OpenAI endpoint")
        key = access_token(provider.api_key_env)
    else:
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
        if provider.kind == "openai_chatgpt":
            raw = {
                "data": [
                    {"id": m["slug"], "name": m.get("display_name", m["slug"])}
                    for m in raw.get("models", [])
                    if m.get("visibility") == "list" and m.get("slug")
                ]
            }
        data = {
            "data": [
                {
                    k: e[k]
                    for k in [
                        "id",
                        "name",
                        "pricing",
                        "context_length",
                        "supported_parameters",
                        "architecture",
                        "benchmarks",
                    ]
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
    if provider.kind == "openrouter":
        try:
            from mlca.config import load

            snapshot(provider, load().catalog.selected, models=models)
        except Exception:
            pass  # A snapshot is a record, never a reason to fail a catalogue load.
    return models


SNAPSHOT_FIELDS = [
    "id",
    "name",
    "group",
    "candidate",
    "router",
    "text_only",
    "context",
    "usd_per_m_input",
    "usd_per_m_output",
    "json_output",
    "tools",
    "aa_coding_index",
    "aa_agentic_index",
]


def snapshot(provider, selected=(), directory=None, models=None):
    """Dated CSV of the free models plus the shortlist: the list a model comparison is chosen from.

    Returns (path, shortlisted IDs the provider did not list)."""
    models = fetch(provider) if models is None else models
    selected = list(selected)
    rows = []
    for m in models:
        if not (m.free or m.id in selected):
            continue
        rows.append(
            {
                "id": m.id,
                "name": m.name,
                "group": "selected" if m.id in selected else "free",
                # Candidates for a comparison: one fixed model that answers in text only.
                "candidate": bool(m.text_only) and not m.router,
                "router": m.router,
                "text_only": m.text_only,
                "context": m.context,
                "usd_per_m_input": m.input_per_million,
                "usd_per_m_output": m.output_per_million,
                "json_output": m.json_output,
                "tools": "tools" in (m.parameters or []),
                "aa_coding_index": m.coding_index,
                "aa_agentic_index": m.agentic_index,
            }
        )
    rows.sort(
        key=lambda r: (r["group"] != "selected", not r["candidate"], -(r["aa_coding_index"] or -1), r["id"])
    )
    directory = Path(directory) if directory else user_config_dir() / "catalog"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{provider.kind}_models_{datetime.date.today().isoformat()}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SNAPSHOT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path, [s for s in selected if s not in {r["id"] for r in rows}]


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
