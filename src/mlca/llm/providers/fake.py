import json
from pathlib import Path
from typing import Any

import yaml

from mlca.errors import MlcaUserError


class FakeProvider:
    """Deterministic scripted provider. No network, implicit responses or model defaults."""

    def __init__(self, config: Any) -> None:
        if not config.script:
            raise MlcaUserError("Fake provider requires a response-script path")
        raw = yaml.safe_load(Path(config.script).read_text(encoding="utf-8"))
        self.responses = raw if isinstance(raw, list) else raw["responses"]
        self.used = set()

    def complete(self, payload: dict, context: Any, index: int) -> dict:
        for n, response in enumerate(self.responses):
            match = response.get("match", {})
            if n in self.used or any(getattr(context, k, None) != v for k, v in match.items()):
                continue
            if "call_index" in response and response["call_index"] != index:
                continue
            self.used.add(n)
            if "error" in response:
                raise MlcaUserError(response["error"])
            content = response.get("text", response.get("response", ""))
            return {
                "text": content if isinstance(content, str) else json.dumps(content),
                "input_tokens": response.get("input_tokens", 0),
                "output_tokens": response.get("output_tokens", 0),
                "cached_tokens": 0,
                "cost_usd": 0.0,
            }
        raise MlcaUserError(f"No fake response for {context.role}/{context.purpose}/{index}")
