import base64
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from filelock import FileLock
from pydantic import BaseModel
from ulid import ULID

from mlca.config import redact, redact_value
from mlca.errors import BudgetError, MlcaUserError
from mlca.paths import atomic_json, canonical

from . import egress, pricing, usage
from .providers.fake import FakeProvider
from .providers.openai_api import OpenAIProvider
from .providers.openai_chatgpt import ChatGPTProvider
from .providers.openai_compatible import CompatibleProvider
from .providers.openrouter import OpenRouterProvider


class RequestContext(BaseModel):
    role: str
    session_id: str
    turn_id: str | None = None
    event_id: str | None = None
    step_id: str | None = None
    action_id: str | None = None
    purpose: str = ""


class LLMResult(BaseModel):
    text: str
    parsed: Any = None
    request_id: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cached_tokens: int | None = None
    cost_usd: float | None = None
    latency_ms: float = 0


def model_output_category(error):
    """Truncated output counts as a Worker attempt; everything else from the provider is infrastructure."""
    return "output_truncated" if getattr(error, "category", None) == "output_truncated" else "provider_error"


RATE_LIMIT_WAITS_S = (5, 15, 30, 60)
FREE_REQUESTS_PER_MINUTE = 16


def pace(provider_config, model, now=time.time, sleep=time.sleep):
    """Space requests so a run stays under the provider's per-minute limit; returns seconds waited.

    The window is shared by every MLCA process on this machine (TUI, bench, MCP)."""
    rpm = provider_config.requests_per_minute
    if (
        rpm is None
        and provider_config.kind == "openrouter"
        and (model.endswith(":free") or model == "openrouter/free")
    ):
        rpm = FREE_REQUESTS_PER_MINUTE
    if not rpm:
        return 0.0
    import hashlib
    import json

    from filelock import FileLock

    from mlca.paths import user_config_dir

    key = hashlib.sha256(
        (
            provider_config.kind + (provider_config.base_url or "") + (provider_config.api_key_env or "")
        ).encode()
    ).hexdigest()[:24]
    path = user_config_dir() / "rate" / (key + ".json")
    path.parent.mkdir(parents=True, exist_ok=True)
    waited = 0.0
    with FileLock(str(path) + ".lock"):
        try:
            stamps = json.loads(path.read_text())
        except (OSError, ValueError):
            stamps = []
        current = now()
        stamps = [t for t in stamps if current - t < 60]
        if len(stamps) >= rpm:
            waited = max(0.0, 60 - (current - stamps[-int(rpm)]))
            sleep(waited)
            current = now()
        stamps.append(current)
        path.write_text(json.dumps(stamps[-int(rpm) * 2 :]))
    return waited


def retry_after(error, index):
    """Seconds to wait after a 429: the provider's Retry-After (capped at 60 s), else a fixed schedule."""
    headers = getattr(getattr(error, "response", None), "headers", None) or {}
    try:
        return min(60.0, max(1.0, float(headers.get("retry-after"))))
    except (TypeError, ValueError):
        return float(RATE_LIMIT_WAITS_S[index])


def structured_setting(provider_config, model):
    """(enabled, source) for JSON-schema output: explicit config wins, else the OpenRouter catalogue."""
    if provider_config.structured_outputs is not None:
        return provider_config.structured_outputs, "config"
    if provider_config.kind != "openrouter":
        return False, "default"
    from .catalog import cached

    models, _ = cached(provider_config)
    if not models:
        return False, "no_catalogue"
    return any(m.id == model and m.json_output for m in models), "catalogue"


class Client:
    def __init__(self, root: Path, config: Any, emit: Any = None) -> None:
        self.root, self.config, self.emit = root, config, emit
        self.providers = {}

    def _provider(self, name: Any) -> Any:
        if name not in self.providers:
            cfg = self.config.providers[name]
            cls = {
                "fake": FakeProvider,
                "openai_api": OpenAIProvider,
                "openai_chatgpt": ChatGPTProvider,
                "openrouter": OpenRouterProvider,
                "openai_compatible": CompatibleProvider,
            }[cfg.kind]
            self.providers[name] = cls(cfg)
        return self.providers[name]

    def complete(
        self,
        role: str,
        messages: list[dict],
        *,
        schema: Any = None,
        images: Any = None,
        context: RequestContext,
        categories: list[str],
        max_attempts: int = 3,
    ) -> LLMResult:
        if getattr(self, "disabled", False):
            raise MlcaUserError("Model calls are disabled in brain mode")
        if role not in self.config.roles:
            raise MlcaUserError(f"Configure a model for role {role} before making requests")
        selected = self.config.roles[role]
        provider_config = self.config.providers[selected.provider]
        # Scrub configured credential values before payload persistence or transmission.
        messages = redact_value(messages, self.config)
        if images:
            for path in images:
                if path.stat().st_size > 8 * 1024 * 1024:
                    raise MlcaUserError("Figure image exceeds the request size limit")
            messages = [
                *messages,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
                            },
                        }
                        for p in images
                    ],
                },
            ]
            categories = [*categories, "figure_image"]
        payload = {
            "model": selected.model,
            "messages": messages,
            "max_completion_tokens": selected.max_output_tokens,
        }
        if provider_config.kind in {"openrouter", "openai_compatible"}:
            payload["max_tokens"] = payload.pop("max_completion_tokens")
        if selected.temperature is not None:
            payload["temperature"] = selected.temperature
        structured, structured_source = structured_setting(provider_config, selected.model)
        if (selected.provider, selected.model) in self._no_structured_endpoint():
            structured, structured_source = False, "no_endpoint_fallback"
        if schema and structured:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                    "strict": False,
                },
            }
        end_user = None
        if provider_config.kind == "openrouter":
            import yaml

            project_file = self.root / ".mlca/project.yaml"
            project_id = (
                yaml.safe_load(project_file.read_text())["project_id"]
                if project_file.exists()
                else "diagnostic:" + context.session_id
            )
            end_user = "mlca-" + hashlib.sha256(project_id.encode()).hexdigest()[:16]
            routing = {}
            if "response_format" in payload:
                routing["require_parameters"] = True
            privacy = self.config.privacy
            if privacy.provider_data_collection is not None:
                routing["data_collection"] = privacy.provider_data_collection
            if privacy.zero_data_retention:
                routing["zdr"] = True
            payload["extra_body"] = {"user": end_user, **({"provider": routing} if routing else {})}
        digest = egress.classify(payload, categories, self.config.privacy.allow_sample_rows)
        provider = self._provider(selected.provider)
        if not 1 <= max_attempts <= 3:
            raise MlcaUserError("Request attempts must be between one and three")
        attempt, rate_waits, downgraded = 0, 0, False
        while attempt < max_attempts:
            attempt += 1
            request_id = str(ULID())
            start = time.monotonic()
            record = {
                **context.model_dump(),
                "principal": getattr(self, "principal", "user"),
                "request_id": request_id,
                "ts": datetime.now(timezone.utc).isoformat(),
                "provider": selected.provider,
                "model": selected.model,
                "attempt": attempt,
                "rate_limit_waits": rate_waits,
                "model_reported": None,
                "provider_reported": None,
                "provider_request_id": None,
                "provider_kind": provider_config.kind,
                "end_user": end_user,
                "reasoning_tokens": None,
                "cache_write_tokens": None,
                "upstream_cost_usd": None,
                "request_settings": {
                    "structured_outputs": bool(schema and structured),
                    "structured_outputs_source": structured_source,
                    "response_format": payload.get("response_format"),
                    "extra_body": payload.get("extra_body"),
                    "temperature": payload.get("temperature"),
                    "max_output_tokens": payload.get("max_tokens", payload.get("max_completion_tokens")),
                    "call_deadline_s": provider_config.call_deadline_s,
                },
                "input_tokens": None,
                "output_tokens": None,
                "cached_tokens": None,
                "cost_usd": None,
                "cost_source": "unknown",
                "latency_ms": 0,
                "status": "pending",
                "reserved_cost_usd": self._bound(payload, selected, provider_config),
            }
            entry = {**digest, **{k: record[k] for k in ["request_id", "role", "provider", "model", "ts"]}}
            with FileLock(str(self.root / ".mlca/model_requests.lock")):
                self._budget(payload, selected, provider_config, context)
                usage.persist(self.root, record, entry)  # Reserve the attempt before network I/O.
                result = None
                error = None
                try:
                    record["pacing_wait_s"] = pace(provider_config, selected.model)
                    if isinstance(provider, FakeProvider):
                        index = sum(r["role"] == role for r in usage.read(self.root)) - 1
                        result = provider.complete(payload, context, index)
                    else:
                        result = provider.complete(payload)
                    self._record_usage(record, result, selected)
                    record["status"] = "ok"
                except Exception as exc:
                    error = exc
                    category = model_output_category(exc)
                    if getattr(exc, "accounting", None):
                        self._record_usage(record, exc.accounting, selected)
                    record.update(
                        status="error",
                        error_type=type(exc).__name__,
                        category=category,
                        status_code=getattr(exc, "status_code", None),
                    )
                    if self.emit:
                        self.emit(
                            "ProviderFailed",
                            {
                                "request_id": request_id,
                                "category": category,
                                "error_type": type(exc).__name__,
                            },
                            step_id=context.step_id,
                        )
                finally:
                    record["latency_ms"] = (time.monotonic() - start) * 1000
                    record["reserved_cost_usd"] = self._bound(payload, selected, provider_config)
                    usage.persist(self.root, record, entry)
                    if self.config.privacy.store_payloads:
                        atomic_json(
                            self.root / ".mlca/llm" / f"{request_id}.json",
                            {
                                "request": payload,
                                "response": redact(result["text"], self.config) if result else None,
                                "status": record["status"],
                            },
                        )
            if error:
                status = getattr(error, "status_code", None)
                routing = (payload.get("extra_body") or {}).get("provider") or {}
                if status == 404 and not downgraded and routing.get("require_parameters"):
                    # No endpoint honours JSON-schema output (the catalogue lists the union of
                    # providers). Retry once without it; MLCA validates JSON itself.
                    downgraded, attempt = True, attempt - 1
                    self._no_structured_endpoint().add((selected.provider, selected.model))
                    payload.pop("response_format", None)
                    routing.pop("require_parameters", None)
                    if not routing:
                        payload["extra_body"].pop("provider", None)
                    structured, structured_source = False, "no_endpoint_fallback"
                    continue
                if status == 429 and rate_waits < len(RATE_LIMIT_WAITS_S):
                    # Rate limits are infrastructure, not model behaviour: wait, do not spend an attempt.
                    wait = retry_after(error, rate_waits)
                    record["rate_limit_wait_s"] = wait
                    usage.persist(self.root, record, entry)
                    time.sleep(wait)
                    rate_waits, attempt = rate_waits + 1, attempt - 1
                    continue
                if attempt < max_attempts and isinstance(status, int) and status >= 500:
                    time.sleep(min(2 ** (attempt - 1), 4))
                    continue
                raise MlcaUserError(
                    redact(str(error), self.config), category=model_output_category(error)
                ) from error
            return LLMResult(
                text=redact(result["text"], self.config),
                request_id=request_id,
                **{
                    k: record[k]
                    for k in ["input_tokens", "output_tokens", "cached_tokens", "cost_usd", "latency_ms"]
                },
            )
        raise MlcaUserError("Provider retry limit exhausted")

    def _no_structured_endpoint(self):
        """(provider, model) pairs with no endpoint for JSON-schema output, learned this session."""
        if not hasattr(self, "_structured_unavailable"):
            self._structured_unavailable = set()
        return self._structured_unavailable

    def _record_usage(self, record, result, selected):
        record.update({k: result[k] for k in ["input_tokens", "output_tokens", "cached_tokens"]})
        for key in ("reasoning_tokens", "cache_write_tokens", "upstream_cost_usd"):
            record[key] = result.get(key)
        for key in ("model_reported", "provider_reported", "provider_request_id"):
            record[key] = redact_value(result.get(key), self.config)
        cost = result.get("cost_usd")
        if cost is not None:
            record.update(cost_usd=float(cost), cost_source="provider")
        elif all(record[k] is not None for k in ("input_tokens", "output_tokens", "cached_tokens")):
            cost = pricing.estimate(
                selected.provider,
                selected.model,
                **{k: record[k] for k in ["input_tokens", "output_tokens", "cached_tokens"]},
            )
            if cost is not None:
                record.update(cost_usd=cost, cost_source="pricing_table")

    def _bound(self, payload: Any, role: Any, provider: Any) -> Any:
        if provider.kind in {"fake", "openai_chatgpt"}:
            return 0.0  # ChatGPT plan limits are enforced upstream; USD cost remains unavailable.
        if provider.request_cost_bound_usd is not None:
            return provider.request_cost_bound_usd
        # Byte count deliberately overestimates typical token counts, including schema overhead.
        return pricing.estimate(
            role.provider, role.model, len(canonical(payload).encode()), role.max_output_tokens
        )

    def _budget(self, payload: Any, role: Any, provider: Any, context: Any) -> Any:
        bound = self._bound(payload, role, provider)
        if bound is None:
            raise BudgetError("Set pricing or request_cost_bound_usd before real model requests")
        records = usage.read(self.root)

        def charged(r: Any) -> Any:
            return max(r.get("cost_usd") or 0, r.get("reserved_cost_usd") or 0)

        session_cost = sum(charged(r) for r in records if r.get("session_id") == context.session_id)
        turn_cost = sum(
            charged(r) for r in records if r.get("turn_id") == context.turn_id and context.turn_id
        )
        if (
            session_cost + bound > self.config.budgets.session_max_usd
            or turn_cost + bound > self.config.budgets.turn_max_usd
        ):
            reason = "Configured model request budget would be exceeded"
            if self.emit:
                self.emit("BudgetStopped", {"reason": reason})
            raise BudgetError(reason)
