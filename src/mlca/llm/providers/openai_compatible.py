from typing import Any

from openai import OpenAI

from mlca.errors import MlcaUserError
from mlca.llm.credentials import resolve


class CompatibleProvider:
    def __init__(self, config: Any) -> None:
        if config.api_key_env == "MLCA_KEYRING_OPENROUTER_KEY" and (
            config.kind != "openrouter" or config.base_url not in {None, "https://openrouter.ai/api/v1"}
        ):
            raise MlcaUserError("OpenRouter sign-in credentials can only be used at OpenRouter")
        key = resolve(config.api_key_env) if config.api_key_env else "local"
        if not key and config.api_key_env == "MLCA_KEYRING_OPENROUTER_KEY":
            raise MlcaUserError("OpenRouter credential unavailable; unlock your OS keyring or sign in again")
        if not key:
            raise MlcaUserError(f"Missing environment variable: {config.api_key_env}")
        self.client = OpenAI(api_key=key, base_url=config.base_url, timeout=config.timeout_s, max_retries=0)

    def complete(self, payload: dict) -> dict:
        response = self.client.chat.completions.create(**payload)
        data = response.model_dump()
        choice = data["choices"][0]
        message = choice["message"]
        usage = data.get("usage") or {}
        result = {
            "text": message.get("content") or "",
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
            "cache_write_tokens": (usage.get("prompt_tokens_details") or {}).get("cache_write_tokens"),
            "upstream_cost_usd": (usage.get("cost_details") or {}).get("upstream_inference_cost"),
            "provider_reported": data.get("provider"),
            "cost_usd": usage.get("cost"),
            "provider_request_id": data.get("id"),
            "model_reported": data.get("model"),
        }

        if message.get("refusal") or choice.get("finish_reason") == "length":
            error = MlcaUserError(
                "Model refused this request"
                if message.get("refusal")
                else "Model response exceeded its token limit"
            )
            error.accounting = result
            raise error
        return result

    def models(self) -> list[str]:
        return [m.id for m in self.client.models.list()]
