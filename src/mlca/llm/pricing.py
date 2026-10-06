from typing import Any

import yaml

from mlca.paths import user_config_dir


def table() -> dict:
    file = user_config_dir() / "pricing.yaml"
    return yaml.safe_load(file.read_text(encoding="utf-8")) or {} if file.exists() else {}


def estimate(provider: str, model: str, input_tokens: int, output_tokens: int, cached_tokens: Any = 0) -> Any:
    entry = table().get(provider, {}).get(model)
    if not entry:
        return None
    return (
        (input_tokens - cached_tokens) * entry["input_per_million"]
        + cached_tokens * entry.get("cached_input_per_million", entry["input_per_million"])
        + output_tokens * entry["output_per_million"]
    ) / 1_000_000
