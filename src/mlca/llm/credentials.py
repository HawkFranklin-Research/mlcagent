"""Session-only keys. Never serialize values or pass them to analysis subprocesses."""

import os
import uuid

_KEYS: dict[str, str] = {}


def remember(value: str) -> str:
    name = "MLCA_SESSION_" + uuid.uuid4().hex.upper() + "_KEY"
    _KEYS[name] = value
    return name


def resolve(name: str | None) -> str | None:
    return _KEYS.get(name) or os.environ.get(name) if name else None


def secret_values() -> list[str]:
    return list(_KEYS.values())


def forget() -> None:
    _KEYS.clear()
