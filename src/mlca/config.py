import os
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

from mlca.errors import MlcaUserError
from mlca.paths import user_config_dir


class ConfigModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProviderConfig(ConfigModel):
    kind: Literal["openai_api", "openrouter", "openai_compatible", "openai_chatgpt", "fake"]
    oauth_client_id: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None
    script: str | None = None
    structured_outputs: bool | None = None
    timeout_s: float = Field(default=90, gt=0)
    request_cost_bound_usd: float | None = Field(default=None, ge=0)


class RoleConfig(ConfigModel):
    provider: str
    model: str
    temperature: float | None = None
    max_output_tokens: int = Field(default=4096, ge=64, le=65536)


class Privacy(ConfigModel):
    allow_sample_rows: bool = False
    store_payloads: bool = True
    provider_data_collection: Literal["allow", "deny"] | None = None
    zero_data_retention: bool = False


class Budgets(ConfigModel):
    turn_max_usd: float = Field(default=1.0, gt=0)
    session_max_usd: float = Field(default=10.0, gt=0)
    worker_max_attempts: int = Field(default=3, ge=1, le=10)


class SandboxConfig(ConfigModel):
    allow_level_b: bool = False


class MCPConfig(ConfigModel):
    mode: Literal["brain", "driver"] = "brain"


class ChatGPTAuth(ConfigModel):
    client_id: str | None = None

    @model_validator(mode="after")
    def own_registration(self):
        if self.client_id and not self.client_id.startswith("oaiapp_"):
            raise ValueError("Use MLCA's own issued oaiapp_ client ID")
        return self


class Config(ConfigModel):
    chatgpt_auth: ChatGPTAuth = Field(default_factory=ChatGPTAuth)
    providers: dict[str, ProviderConfig] = Field(default_factory=dict)
    roles: dict[str, RoleConfig] = Field(default_factory=dict)
    privacy: Privacy = Field(default_factory=Privacy)
    budgets: Budgets = Field(default_factory=Budgets)
    sandbox: SandboxConfig = Field(default_factory=SandboxConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)

    @model_validator(mode="after")
    def roles_exist(self) -> Any:
        for name, role in self.roles.items():
            if (
                name not in {"navigator", "worker", "inspector", "illustrator"}
                or role.provider not in self.providers
            ):
                raise ValueError(f"Unknown role or provider: {name}")
        for provider in self.providers.values():
            if provider.kind == "openai_chatgpt" and (
                not provider.oauth_client_id
                or not provider.oauth_client_id.startswith("oaiapp_")
                or provider.base_url not in {None, "https://api.openai.com/v1"}
            ):
                raise ValueError(
                    "ChatGPT plan requests require MLCA registration and the public OpenAI endpoint"
                )
            if provider.api_key_env and not provider.api_key_env.replace("_", "").isalnum():
                raise ValueError("api_key_env must name an environment variable")
            if provider.base_url:
                from urllib.parse import urlparse

                url = urlparse(provider.base_url)
                if url.username or url.password or url.query or url.fragment:
                    raise ValueError("base_url cannot contain credentials, query parameters or fragments")
                if url.scheme != "https" and url.hostname not in {"localhost", "127.0.0.1", "::1"}:
                    raise ValueError("Remote provider base_url must use HTTPS")
        return self


def merge(base: dict, overrides: dict) -> dict:
    result = dict(base)
    for key, value in overrides.items():
        result[key] = merge(result.get(key, {}), value) if isinstance(value, dict) else value
    return result


def load(root: Path | None = None) -> Config:
    file = user_config_dir() / "config.yaml"
    data = yaml.safe_load(file.read_text(encoding="utf-8")) or {} if file.exists() else {}
    if root and (root / ".mlca/project.yaml").exists():
        project = yaml.safe_load((root / ".mlca/project.yaml").read_text(encoding="utf-8"))
        data = merge(data, project.get("config", {}))
    try:
        return Config.model_validate(data)
    except ValueError as exc:
        raise MlcaUserError(f"Invalid configuration: {exc}") from exc


def save(config: Config) -> Path:
    path = user_config_dir() / "config.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(config.model_dump(mode="json"), sort_keys=False), encoding="utf-8")
    path.chmod(0o600)
    return path


def redact(text: str, config: Config | None = None) -> str:
    from mlca.llm.credentials import resolve, secret_values

    if config:
        for provider in config.providers.values():
            if provider.api_key_env and provider.api_key_env.startswith("MLCA_KEYRING_"):
                resolve(provider.api_key_env)
    for value in secret_values():
        if value:
            text = text.replace(value, "[REDACTED]")
    names = [p.api_key_env for p in config.providers.values() if p.api_key_env] if config else []
    names += [
        name
        for name in os.environ
        if any(marker in name.upper() for marker in ("KEY", "TOKEN", "SECRET", "PASSWORD"))
    ]
    for name in set(names):
        value = os.environ.get(name)
        if value:
            text = text.replace(value, "[REDACTED]")
    return text


def redact_value(value: object, config: Config | None = None) -> object:
    """Redact strings recursively without changing JSON syntax or scalar types."""
    if isinstance(value, str):
        return redact(value, config)
    if isinstance(value, list):
        return [redact_value(item, config) for item in value]
    if isinstance(value, dict):
        return {key: redact_value(item, config) for key, item in value.items()}
    return value
