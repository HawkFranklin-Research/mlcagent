"""Official ChatGPT plan-use OAuth with MLCA's configured registration only."""

import hashlib
import json
import secrets
import time
import urllib.parse
import urllib.request
import uuid

import jwt
from filelock import FileLock

from mlca.errors import MlcaUserError
from mlca.paths import atomic_json, user_config_dir

from .credentials import _KEYS
from .openrouter_auth import Flow, secure_backend

ISSUER = "https://auth.openai.com"
AUTHORIZE = ISSUER + "/api/accounts/authorize"
TOKEN = ISSUER + "/api/accounts/oauth/token"
RESOURCE = "https://api.openai.com/v1"
SCOPES = "openid profile email offline_access resource.invoke chatgpt.tokens.use.direct"
SERVICE = "mlca.openai.chatgpt"


def reference(client_id):
    return "MLCA_KEYRING_CHATGPT_" + hashlib.sha256(client_id.encode()).hexdigest().upper() + "_TOKEN"


def remember_tokens(data, name):
    for field in ("access_token", "refresh_token", "id_token"):
        if isinstance(data.get(field), str):
            _KEYS[name + "_" + field.upper()] = data[field]


def token_request(payload):
    request = urllib.request.Request(
        TOKEN,
        urllib.parse.urlencode(payload).encode(),
        {"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.loads(response.read(1024 * 1024))
        if not isinstance(data, dict):
            raise ValueError()
        return data
    except Exception:
        raise MlcaUserError(
            "ChatGPT authorization/refresh failed; sign in again. Credentials were not logged."
        ) from None


def identity(id_token, client_id, nonce=None):
    try:
        key = jwt.PyJWKClient(ISSUER + "/.well-known/jwks.json").get_signing_key_from_jwt(id_token).key
        claims = jwt.decode(
            id_token,
            key,
            algorithms=["RS256", "ES256"],
            audience=client_id,
            issuer=ISSUER,
            options={"require": ["exp", "sub", "aud", "iss"]},
        )
        if nonce is not None and not secrets.compare_digest(str(claims.get("nonce", "")), nonce):
            raise ValueError()
        return claims
    except Exception:
        raise MlcaUserError("ChatGPT identity validation failed; no credentials were activated") from None


def host_id():
    path = user_config_dir() / "chatgpt-host.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    with FileLock(str(path) + ".lock"):
        if path.exists():
            return json.loads(path.read_text())["host_id"]
        value = "urn:uuid:" + str(uuid.uuid4())
        atomic_json(path, {"host_id": value})
        return value


def load_profile(name):
    try:
        raw = secure_backend().get_password(SERVICE, name)
        data = json.loads(raw) if raw else None
        if data:
            remember_tokens(data, name)
        return data
    except Exception:
        raise MlcaUserError(
            "ChatGPT secure credentials unavailable; unlock the OS keyring or sign in again"
        ) from None


def save_profile(data):
    name = reference(data["client_id"])
    remember_tokens(data, name)
    try:
        secure_backend().set_password(SERVICE, name, json.dumps(data))
    except Exception:
        raise MlcaUserError("ChatGPT credentials could not be saved to the secure OS keyring") from None
    return name


class OpenAIFlow(Flow):
    def __init__(self, client_id):
        if not client_id or not client_id.startswith("oaiapp_"):
            raise MlcaUserError("Register MLCA and configure its own issued OpenAI client ID before sign-in")
        secure_backend()
        super().__init__(callback_path="/auth/callback")
        self.client_id = client_id
        self.nonce = secrets.token_urlsafe(32)
        self.host = host_id()
        self.redirect = f"http://127.0.0.1:{self.server.server_port}/auth/callback"
        old = urllib.parse.parse_qs(urllib.parse.urlsplit(self.url).query)
        params = {
            "client_id": client_id,
            "ext_agent_host_id": self.host,
            "response_type": "code",
            "redirect_uri": self.redirect,
            "scope": SCOPES,
            "resource": RESOURCE,
            "state": self.state,
            "nonce": self.nonce,
            "code_challenge_method": "S256",
            "code_challenge": old["code_challenge"][0],
        }
        self.url = AUTHORIZE + "?" + urllib.parse.urlencode(params)

    def accept(self, value):
        parsed = urllib.parse.urlsplit(value)
        query = urllib.parse.parse_qs(parsed.query)
        if query.get("client_id") not in (None, [self.client_id]):
            raise MlcaUserError("Callback client ID differs from MLCA registration")
        if query.get("state") == [self.state] and query.get("error"):
            self.close()
            raise MlcaUserError("ChatGPT authorization declined")
        super().accept(value)

    def exchange(self):
        if not self.code or self.closed.is_set() or time.monotonic() >= self.deadline:
            raise MlcaUserError("ChatGPT sign-in expired or cancelled")
        payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "code": self.code,
            "code_verifier": self.verifier,
            "redirect_uri": self.redirect,
            "resource": RESOURCE,
        }
        self.code = None
        self.close()
        data = token_request(payload)
        remember_tokens(data, reference(self.client_id))
        claims = identity(data.get("id_token", ""), self.client_id, self.nonce)
        old = load_profile(reference(self.client_id))
        if old and claims["sub"] != old["subject"]:
            raise MlcaUserError("ChatGPT account differs from the selected registration")
        scopes = data.get("scope", "").split()
        if "chatgpt.tokens.use.direct" not in scopes:
            raise MlcaUserError("ChatGPT plan usage was not approved; no inference is authorized")
        if (
            not data.get("access_token")
            or not data.get("refresh_token")
            or data.get("token_type", "").lower() != "bearer"
        ):
            raise MlcaUserError("Incomplete ChatGPT token grant")
        return {
            **{k: data[k] for k in ("access_token", "refresh_token", "id_token")},
            "client_id": self.client_id,
            "subject": claims["sub"],
            "host_id": self.host,
            "scopes": scopes,
            "expires_at": time.time() + int(data["expires_in"]),
        }


def access_token(name):
    directory = user_config_dir() / "auth-locks"
    directory.mkdir(parents=True, exist_ok=True)
    with FileLock(str(directory / (hashlib.sha256(name.encode()).hexdigest() + ".lock"))):
        saved = load_profile(name)
        if not saved:
            raise MlcaUserError("Sign in with ChatGPT before making requests")
        if "chatgpt.tokens.use.direct" not in saved.get("scopes", []):
            raise MlcaUserError("ChatGPT plan usage is not authorized")
        if saved["expires_at"] <= time.time() + 60:
            data = token_request(
                {
                    "grant_type": "refresh_token",
                    "client_id": saved["client_id"],
                    "refresh_token": saved["refresh_token"],
                    "resource": RESOURCE,
                }
            )
            remember_tokens(data, name)
            scopes = data.get("scope", " ".join(saved["scopes"])).split()
            if "chatgpt.tokens.use.direct" not in scopes or not data.get("access_token"):
                raise MlcaUserError("ChatGPT plan permission expired; authorize again")
            if data.get("id_token"):
                claims = identity(data["id_token"], saved["client_id"])
                if claims["sub"] != saved["subject"]:
                    raise MlcaUserError("ChatGPT refresh identity mismatch")
            saved = {
                **saved,
                **{k: data[k] for k in ("access_token", "refresh_token", "id_token") if data.get(k)},
                "scopes": scopes,
                "expires_at": time.time() + int(data["expires_in"]),
            }
            save_profile(saved)
        return saved["access_token"]


def signout(client_id):
    name = reference(client_id)
    saved = load_profile(name)
    revoked = False
    if saved:
        try:
            with urllib.request.urlopen(ISSUER + "/.well-known/openid-configuration", timeout=10) as response:
                endpoint = json.loads(response.read(65536))["revocation_endpoint"]
            if not endpoint.startswith(ISSUER + "/"):
                raise ValueError()
            request = urllib.request.Request(
                endpoint,
                urllib.parse.urlencode(
                    {
                        "token": saved["refresh_token"],
                        "token_type_hint": "refresh_token",
                        "client_id": client_id,
                    }
                ).encode(),
                {"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=10):
                revoked = True
        except Exception:
            pass
        secure_backend().delete_password(SERVICE, name)
    for entry in list(_KEYS):
        if entry.startswith(name):
            del _KEYS[entry]
    return revoked
