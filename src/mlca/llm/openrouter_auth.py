"""User-initiated OpenRouter PKCE. No model calls, account identity guesses or file secrets."""

import base64
import hashlib
import json
import secrets
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from mlca.errors import MlcaUserError

REFERENCE = "MLCA_KEYRING_OPENROUTER_KEY"
SERVICE = "mlca.openrouter"
ACCOUNT = "default"


def secure_backend():
    import keyring

    backend = keyring.get_keyring()
    # Reject plaintext, null, chained and third-party fallback backends.
    if type(backend).__module__ not in {
        "keyring.backends.SecretService",
        "keyring.backends.macOS",
        "keyring.backends.Windows",
    }:
        raise MlcaUserError(
            "Secure OS keyring unavailable; use session-only sign-in or a manual environment key"
        )
    return backend


def stored_key():
    try:
        return secure_backend().get_password(SERVICE, ACCOUNT)
    except Exception:
        return None


def store_key(key, persistent=True):
    from .credentials import _KEYS, remember

    if persistent:
        try:
            secure_backend().set_password(SERVICE, ACCOUNT, key)
        except Exception:
            raise MlcaUserError("Could not save to the secure OS keyring; retry session-only") from None
        _KEYS[REFERENCE] = key  # Keep redaction aware of every key used by this process.
        return REFERENCE
    return remember(key)


def signout():
    from .credentials import _KEYS

    try:
        backend = secure_backend()
        if backend.get_password(SERVICE, ACCOUNT):
            backend.delete_password(SERVICE, ACCOUNT)
    except Exception:
        raise MlcaUserError("Could not clear the OS keyring; unlock it and retry signout") from None
    value = _KEYS.pop(REFERENCE, None)
    if value:
        for name in list(_KEYS):
            if _KEYS[name] == value:
                del _KEYS[name]


class Flow:
    def __init__(self, headless=False, callback_path="/callback"):
        self.callback_path = callback_path
        self.verifier = secrets.token_urlsafe(48)
        self.state = secrets.token_urlsafe(32)
        self.deadline = time.monotonic() + 600
        self.server = None
        self.code = None
        self.closed = threading.Event()
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(self.verifier.encode()).digest()).decode().rstrip("=")
        )
        params = {"code_challenge": challenge, "code_challenge_method": "S256", "key_label": "MLCA"}
        if not headless:
            flow = self

            class Callback(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass  # Callback URL contains a secret authorization code.

                def do_GET(self):
                    try:
                        flow.accept("http://127.0.0.1:" + str(flow.server.server_port) + self.path)
                    except MlcaUserError:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b"Invalid or expired MLCA callback.")
                        return
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(b"Authorization received. Return to MLCA.")

            class CallbackServer(HTTPServer):
                def get_request(self):
                    connection, address = super().get_request()
                    connection.settimeout(1)
                    return connection, address

            self.server = CallbackServer(("127.0.0.1", 0), Callback)
            self.server.timeout = 0.25
            params.update(
                callback_url=f"http://127.0.0.1:{self.server.server_port}{self.callback_path}",
                state=self.state,
            )
        self.url = "https://openrouter.ai/auth?" + urllib.parse.urlencode(params)

    def accept(self, value):
        if self.closed.is_set() or time.monotonic() >= self.deadline or self.code:
            raise MlcaUserError("Sign-in expired or already used; start again")
        value = value.strip()
        if self.server:
            parsed = urllib.parse.urlsplit(value)
            query = urllib.parse.parse_qs(parsed.query)
            expected = f"127.0.0.1:{self.server.server_port}"
            if (
                parsed.scheme != "http"
                or parsed.netloc != expected
                or parsed.path != self.callback_path
                or query.get("state") != [self.state]
                or len(query.get("code", [])) != 1
            ):
                raise MlcaUserError("Invalid sign-in callback or state")
            value = query["code"][0]
        elif "://" in value:
            raise MlcaUserError("Paste the displayed authorization code, not a URL")
        if not value or len(value) > 4096 or any(c.isspace() for c in value):
            raise MlcaUserError("Invalid authorization code")
        self.code = value

    def wait(self):
        if not self.server:
            raise MlcaUserError("Headless sign-in needs a pasted authorization code")
        while not self.code and not self.closed.is_set() and time.monotonic() < self.deadline:
            self.server.handle_request()
        if not self.code:
            raise MlcaUserError("Sign-in cancelled or timed out")

    def exchange(self):
        if not self.code or self.closed.is_set() or time.monotonic() >= self.deadline:
            raise MlcaUserError("Sign-in expired or has no authorization code")
        payload = {"code": self.code, "code_verifier": self.verifier, "code_challenge_method": "S256"}
        # Consume before transmission: retry by starting a fresh flow.
        self.code = None
        self.close()
        request = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/keys",
            json.dumps(payload).encode(),
            {"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.loads(response.read(65536))
            key = data.get("key")
            if not isinstance(key, str) or not key or len(key) > 8192:
                raise ValueError()
        except Exception:
            raise MlcaUserError(
                "OpenRouter sign-in exchange failed; start again (no credentials were logged)"
            ) from None
        from .credentials import remember

        remember(key)  # Redact even if keyring storage subsequently fails.
        return key

    def close(self):
        self.closed.set()
        if self.server:
            self.server.server_close()

    def open_browser(self):
        return webbrowser.open(self.url)


def configure_free(config, reference):
    from mlca.config import Config, ProviderConfig, RoleConfig

    from .catalog import Model, save_prices

    data = config.model_dump()
    data["providers"]["openrouter_free"] = ProviderConfig(
        kind="openrouter", api_key_env=reference
    ).model_dump()
    for role in ("navigator", "worker"):
        old = config.roles.get(role)
        data["roles"][role] = RoleConfig.model_validate(
            {**(old.model_dump() if old else {}), "provider": "openrouter_free", "model": "openrouter/free"}
        ).model_dump()
    save_prices("openrouter_free", [Model("openrouter/free", "Free Models Router", 0, 0, free=True)])
    return Config.model_validate(data)
