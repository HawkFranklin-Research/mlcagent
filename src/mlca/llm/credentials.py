"""Environment, session and author-approved secure OS keyring references. Never serialize values or pass them to analysis subprocesses."""

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
    if name.startswith("MLCA_KEYRING_API_") and name not in _KEYS:
        try:
            from .openrouter_auth import secure_backend

            value = secure_backend().get_password("mlca.api_keys", name)
            if value:
                _KEYS[name] = value
        except Exception:
            return None
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


def remember_secure(value: str, provider_name: str) -> str:
    import hashlib

    from mlca.errors import MlcaUserError

    from .openrouter_auth import secure_backend

    name = "MLCA_KEYRING_API_" + hashlib.sha256(provider_name.encode()).hexdigest().upper() + "_KEY"
    remember(value)  # Redact before any persistence attempt.
    try:
        secure_backend().set_password("mlca.api_keys", name, value)
    except Exception:
        raise MlcaUserError(
            "Secure key storage failed; disable Remember API keys for session-only storage"
        ) from None
    _KEYS[name] = value
    return name
