import os
from typing import Any

from openai import OpenAI

from mlca.errors import MlcaUserError


class CompatibleProvider:
    def __init__(self, config: Any) -> None:
        key = os.environ.get(config.api_key_env) if config.api_key_env else "local"
        if not key:
            raise MlcaUserError(f"Missing environment variable: {config.api_key_env}")
        self.client = OpenAI(api_key=key, base_url=config.base_url, timeout=config.timeout_s, max_retries=0)

    def complete(self, payload: dict) -> dict:
        response = self.client.chat.completions.create(**payload)
        data = response.model_dump()
        choice = data["choices"][0]
        message = choice["message"]
        if message.get("refusal"):
            raise MlcaUserError("Model refused this request")
        if choice.get("finish_reason") == "length":
            raise MlcaUserError("Model response exceeded its token limit")
        usage = data.get("usage") or {}
        return {
            "text": message.get("content") or "",
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "cached_tokens": (usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
            "cost_usd": usage.get("cost"),
            "provider_request_id": data.get("id"),
            "model_reported": data.get("model"),
        }

    def models(self) -> list[str]:
        return [m.id for m in self.client.models.list()]
