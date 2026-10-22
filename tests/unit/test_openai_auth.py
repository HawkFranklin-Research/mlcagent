import time
import urllib.parse
from types import SimpleNamespace as NS

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from mlca.config import Config, ProviderConfig
from mlca.errors import MlcaUserError
from mlca.llm import credentials
from mlca.llm import openai_auth as auth


@pytest.fixture
def backend(monkeypatch):
    class Backend:
        values = {}

        def set_password(self, service, name, value):
            self.values[(service, name)] = value

        def get_password(self, service, name):
            return self.values.get((service, name))

        def delete_password(self, service, name):
            self.values.pop((service, name), None)

    backend = Backend()
    monkeypatch.setattr(auth, "secure_backend", lambda: backend)
    credentials.forget()
    yield backend
    credentials.forget()


def profile():
    return {
        "client_id": "oaiapp_mlca",
        "access_token": "access-canary",
        "refresh_token": "refresh-canary",
        "id_token": "id-canary",
        "scopes": ["chatgpt.tokens.use.direct"],
        "expires_at": time.time() + 3600,
        "subject": "user",
    }


def test_registration_gated_and_pkce_state(backend):
    with pytest.raises(MlcaUserError):
        auth.OpenAIFlow("borrowed-client")
    with pytest.raises(ValueError):
        Config(chatgpt_auth={"client_id": "borrowed-client"})
    flow = auth.OpenAIFlow("oaiapp_mlca")
    try:
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(flow.url).query)
        assert query["client_id"] == ["oaiapp_mlca"]
        assert query["resource"] == [auth.RESOURCE]
        assert query["redirect_uri"][0].endswith("/auth/callback")
        assert "chatgpt.tokens.use.direct" in query["scope"][0]
        with pytest.raises(MlcaUserError):
            flow.accept(flow.redirect + "?code=c&state=wrong")
        with pytest.raises(MlcaUserError):
            flow.accept(flow.redirect + f"?code=c&state={flow.state}&client_id=oaiapp_other")
    finally:
        flow.close()


def test_id_signature_nonce_and_identity(monkeypatch):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(jwt.PyJWKClient, "get_signing_key_from_jwt", lambda *args: NS(key=key.public_key()))
    claims = {"sub": "user", "iss": auth.ISSUER, "aud": "oaiapp_mlca", "exp": time.time() + 60, "nonce": "n"}
    encoded = jwt.encode(claims, key, algorithm="RS256")
    assert auth.identity(encoded, "oaiapp_mlca", "n")["sub"] == "user"
    with pytest.raises(MlcaUserError):
        auth.identity(encoded, "oaiapp_mlca", "bad")
    with pytest.raises(MlcaUserError):
        auth.identity(encoded, "oaiapp_other", "n")


def test_exchange_requires_plan_grant(backend, monkeypatch):
    monkeypatch.setattr(auth, "identity", lambda *args: {"sub": "user"})
    response = {**profile(), "token_type": "Bearer", "expires_in": 3600, "scope": "openid"}
    monkeypatch.setattr(auth, "token_request", lambda payload: response)
    flow = auth.OpenAIFlow("oaiapp_mlca")
    flow.accept(flow.redirect + f"?code=c&state={flow.state}")
    with pytest.raises(MlcaUserError, match="not approved"):
        flow.exchange()
    assert backend.values == {}
    response["scope"] = "openid chatgpt.tokens.use.direct"
    flow = auth.OpenAIFlow("oaiapp_mlca")
    flow.accept(flow.redirect + f"?code=c&state={flow.state}")
    data = flow.exchange()
    assert auth.save_profile(data) == auth.reference("oaiapp_mlca")
    from mlca.config import redact

    assert redact("access-canary refresh-canary") == "[REDACTED] [REDACTED]"


def test_rotating_refresh_and_no_disk_tokens(backend, monkeypatch, tmp_path):
    saved = profile()
    saved["expires_at"] = 0
    reference = auth.save_profile(saved)
    monkeypatch.setattr(
        auth,
        "token_request",
        lambda payload: {"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600},
    )
    assert auth.access_token(reference) == "new-access"
    assert auth.load_profile(reference)["refresh_token"] == "new-refresh"
    for path in tmp_path.rglob("*"):
        if path.is_file():
            assert b"new-refresh" not in path.read_bytes()


def test_responses_only_accepts_completed_stream(monkeypatch):
    from mlca.llm.providers import openai_chatgpt as provider

    monkeypatch.setattr(provider, "access_token", lambda *args: "access")
    events = []
    requests = []

    class Stream:
        def __enter__(self):
            return iter(events)

        def __exit__(self, *args):
            pass

    class Client:
        def __init__(self, **kwargs):
            self.responses = NS(create=self.create)

        def create(self, **kwargs):
            requests.append(kwargs)
            return Stream()

        def close(self):
            pass

    monkeypatch.setattr(provider, "OpenAI", Client)
    adapter = provider.ChatGPTProvider(
        ProviderConfig(
            kind="openai_chatgpt", oauth_client_id="oaiapp_mlca", api_key_env=auth.reference("oaiapp_mlca")
        )
    )
    payload = {
        "model": "account-model",
        "messages": [{"role": "user", "content": "Hi"}],
        "max_completion_tokens": 64,
    }
    with pytest.raises(MlcaUserError, match="before response.completed"):
        adapter.complete(payload)
    terminal = {
        "model": "actual",
        "output": [{"content": [{"type": "output_text", "text": "OK"}]}],
        "usage": {"input_tokens": 1, "output_tokens": 4, "output_tokens_details": {"reasoning_tokens": 2}},
    }
    events.append(NS(type="response.completed", response=NS(model_dump=lambda: terminal)))
    result = adapter.complete(payload)
    assert result["text"] == "OK" and result["reasoning_tokens"] == 2
    assert result["output_tokens"] == 4 and result["cache_write_tokens"] is None
    assert requests[-1]["store"] is False and requests[-1]["stream"] is True
    events[:] = [NS(type="response.failed")]
    with pytest.raises(MlcaUserError):
        adapter.complete(payload)


def test_first_sign_in_registers_mlca_and_uses_the_issued_id(backend, monkeypatch):
    flow = auth.OpenAIFlow()
    try:
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(flow.url).query)
        assert query["client_id"] == [auth.REGISTRATION]
        assert query["agent_name_hint"] == [auth.AGENT_NAME]
        assert query["redirect_uri"][0].startswith("http://127.0.0.1:")
        with pytest.raises(MlcaUserError, match="issued MLCA client ID"):
            flow.accept(flow.redirect + f"?code=c&state={flow.state}")
        with pytest.raises(MlcaUserError, match="issued MLCA client ID"):
            flow.accept(flow.redirect + f"?code=c&state={flow.state}&client_id=borrowed")
        with pytest.raises(MlcaUserError):
            flow.accept(flow.redirect + "?code=c&state=wrong&client_id=oaiapp_new")
        assert flow.client_id is None
        flow.accept(flow.redirect + f"?code=c&state={flow.state}&client_id=oaiapp_new")
        assert flow.client_id == "oaiapp_new"
    finally:
        flow.close()
    sent = {}
    monkeypatch.setattr(auth, "identity", lambda token, client, nonce=None: {"sub": "user"})
    monkeypatch.setattr(
        auth,
        "token_request",
        lambda payload: (
            sent.update(payload)
            or {**profile(), "token_type": "Bearer", "expires_in": 3600, "scope": "chatgpt.tokens.use.direct"}
        ),
    )
    flow = auth.OpenAIFlow()
    flow.accept(flow.redirect + f"?code=c&state={flow.state}&client_id=oaiapp_new")
    data = flow.exchange()
    assert sent["client_id"] == data["client_id"] == "oaiapp_new"


def test_signin_saves_the_issued_client_id(monkeypatch):
    import mlca.cli.main as cli
    import mlca.config as config_module
    import mlca.llm.openai_auth as module

    class Flow:
        url = "https://auth.openai.com/api/accounts/authorize?client_id=dynamic_agent_client"

        def __init__(self, client_id=None):
            assert client_id is None

        def open_browser(self):
            pass

        def wait(self):
            pass

        def exchange(self):
            return {**profile(), "client_id": "oaiapp_new"}

        def close(self):
            pass

    saved = {}
    monkeypatch.setattr(cli, "load", lambda: Config())
    monkeypatch.setattr(cli.typer, "confirm", lambda *a, **k: True)
    monkeypatch.setattr(module, "OpenAIFlow", Flow)
    monkeypatch.setattr(module, "save_profile", lambda data: "reference")
    monkeypatch.setattr(config_module, "save", lambda config: saved.setdefault("config", config))
    cli.openai_signin(headless=False)
    assert saved["config"].chatgpt_auth.client_id == "oaiapp_new"
