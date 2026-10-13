from openai import OpenAI

from mlca.errors import MlcaUserError
from mlca.llm.openai_auth import RESOURCE, access_token, reference


class ChatGPTProvider:
    def __init__(self, config):
        if (
            config.base_url not in {None, RESOURCE}
            or not config.oauth_client_id
            or config.api_key_env != reference(config.oauth_client_id)
        ):
            raise MlcaUserError("ChatGPT requires MLCA registration and the public OpenAI Responses API")
        self.config = config

    def complete(self, payload):
        request = {
            "model": payload["model"],
            "input": [],
            "max_output_tokens": payload.get("max_completion_tokens", payload.get("max_tokens")),
            "store": False,
            "stream": True,
        }
        for message in payload["messages"]:
            content = message["content"]
            if isinstance(content, list):
                content = [
                    {"type": "input_image", "image_url": c["image_url"]["url"]}
                    if c["type"] == "image_url"
                    else {"type": "input_text", "text": c["text"]}
                    for c in content
                ]
            request["input"].append({"role": message["role"], "content": content})
        if "temperature" in payload:
            request["temperature"] = payload["temperature"]
        if "response_format" in payload:
            fmt = payload["response_format"]["json_schema"]
            request["text"] = {"format": {"type": "json_schema", **fmt}}
        client = OpenAI(
            api_key=access_token(self.config.api_key_env),
            base_url=RESOURCE,
            timeout=self.config.timeout_s,
            max_retries=0,
        )
        terminal = None
        try:
            with client.responses.create(**request) as stream:
                for event in stream:
                    if event.type == "response.completed":
                        terminal = event.response.model_dump()
                    elif event.type in {"response.failed", "response.incomplete", "error"}:
                        raise MlcaUserError("ChatGPT response failed, was incomplete or reached a plan limit")
        finally:
            client.close()
        if terminal is None:
            raise MlcaUserError("ChatGPT stream ended before response.completed")
        output = terminal.get("output", [])
        content = [c for item in output for c in item.get("content", [])]
        if any(c.get("type") == "refusal" for c in content):
            raise MlcaUserError("ChatGPT refused the request")
        usage = terminal.get("usage") or {}
        return {
            "text": "".join(c.get("text", "") for c in content if c.get("type") == "output_text"),
            "model_reported": terminal.get("model"),
            "provider_request_id": terminal.get("id"),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "cached_tokens": (usage.get("input_tokens_details") or {}).get("cached_tokens"),
            "reasoning_tokens": (usage.get("output_tokens_details") or {}).get("reasoning_tokens"),
            "cache_write_tokens": (usage.get("input_tokens_details") or {}).get("cache_write_tokens"),
            "upstream_cost_usd": None,
            "provider_reported": None,
            "cost_usd": None,
        }
