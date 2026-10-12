"""Session-only keys. Never serialize values or pass them to analysis subprocesses."""

import os
import uuid

_KEYS: dict[str, str] = {}


def remember(value: str) -> str:
    name = "MLCA_SESSION_" + uuid.uuid4().hex.upper() + "_KEY"
    _KEYS[name] = value
    return name


def resolve(name: str | None) -> str | None:
    if not name:
        return None
    if name == "MLCA_KEYRING_OPENROUTER_KEY" and name not in _KEYS:
        from .openrouter_auth import stored_key

        value = stored_key()
        if value:
            _KEYS[name] = value
    return _KEYS.get(name) or os.environ.get(name)


def secret_values() -> list[str]:
    return list(_KEYS.values())


def forget() -> None:
    _KEYS.clear()


def forget_reference(name: str | None) -> None:
    value = _KEYS.pop(name, None)
    if value:
        for other in list(_KEYS):
            if _KEYS[other] == value:
                del _KEYS[other]
