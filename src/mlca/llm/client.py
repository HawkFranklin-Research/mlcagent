import base64
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
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    cost_usd: float | None = None
    latency_ms: float = 0


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
        if schema and provider_config.structured_outputs:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                    "strict": False,
                },
            }
        digest = egress.classify(payload, categories, self.config.privacy.allow_sample_rows)
        provider = self._provider(selected.provider)
        for attempt in range(1, 4):
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
                "model_reported": None,
                "request_settings": {
                    "temperature": payload.get("temperature"),
                    "max_output_tokens": payload.get("max_tokens", payload.get("max_completion_tokens")),
                },
                "input_tokens": 0,
                "output_tokens": 0,
                "cached_tokens": 0,
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
                    if isinstance(provider, FakeProvider):
                        index = sum(r["role"] == role for r in usage.read(self.root)) - 1
                        result = provider.complete(payload, context, index)
                    else:
                        result = provider.complete(payload)
                    record.update({k: result[k] for k in ["input_tokens", "output_tokens", "cached_tokens"]})
                    record["model_reported"] = result.get("model_reported")
                    cost = result.get("cost_usd")
                    if cost is not None:
                        record.update(cost_usd=float(cost), cost_source="provider")
                    else:
                        cost = pricing.estimate(
                            selected.provider,
                            selected.model,
                            **{k: record[k] for k in ["input_tokens", "output_tokens", "cached_tokens"]},
                        )
                        if cost is not None:
                            record.update(cost_usd=cost, cost_source="pricing_table")
                    record["status"] = "ok"
                except Exception as exc:
                    error = exc
                    record.update(status="error", error_type=type(exc).__name__)
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
                if attempt < 3 and (status == 429 or (isinstance(status, int) and status >= 500)):
                    time.sleep(min(2 ** (attempt - 1), 4))
                    continue
                raise MlcaUserError(redact(str(error), self.config)) from error
            return LLMResult(
                text=redact(result["text"], self.config),
                request_id=request_id,
                **{
                    k: record[k]
                    for k in ["input_tokens", "output_tokens", "cached_tokens", "cost_usd", "latency_ms"]
                },
            )
        raise MlcaUserError("Provider retry limit exhausted")

    def _bound(self, payload: Any, role: Any, provider: Any) -> Any:
        if provider.kind == "fake":
            return 0.0
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
