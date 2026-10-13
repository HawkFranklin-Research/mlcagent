import base64
import hashlib
import io
import json
import urllib.parse

import pytest

from mlca.config import Config, ProviderConfig, RoleConfig, redact
from mlca.errors import MlcaUserError
from mlca.llm import credentials
from mlca.llm import openrouter_auth as auth


@pytest.fixture(autouse=True)
def clean_keys():
    credentials.forget()
    yield
    credentials.forget()


def test_pkce_headless_and_single_use(monkeypatch):
    flow = auth.Flow(headless=True)
    params = urllib.parse.parse_qs(urllib.parse.urlsplit(flow.url).query)
    expected = base64.urlsafe_b64encode(hashlib.sha256(flow.verifier.encode()).digest()).decode().rstrip("=")
    assert params["code_challenge"] == [expected]
    assert params["code_challenge_method"] == ["S256"]
    assert "callback_url" not in params
    seen = []

    def exchange(request, timeout):
        seen.append(json.loads(request.data))
        return io.BytesIO(b'{"key":"oauth-key-canary"}')

    monkeypatch.setattr(auth.urllib.request, "urlopen", exchange)
    flow.accept("one-use-code")
    assert flow.exchange() == "oauth-key-canary"
    assert seen[0]["code_verifier"] == flow.verifier
    assert redact("oauth-key-canary") == "[REDACTED]"
    with pytest.raises(MlcaUserError):
        flow.exchange()


def test_callback_origin_path_state_and_duplicate():
    flow = auth.Flow()
    try:
        port = flow.server.server_port
        base = f"http://127.0.0.1:{port}/callback"
        for url in [
            f"{base}?code=c&state=wrong",
            f"http://evil.example/callback?code=c&state={flow.state}",
            f"{base}?code=c&code=d&state={flow.state}",
        ]:
            with pytest.raises(MlcaUserError):
                flow.accept(url)
        flow.accept(f"{base}?code=c&state={flow.state}")
        assert flow.code == "c"
        with pytest.raises(MlcaUserError):
            flow.accept(f"{base}?code=c&state={flow.state}")
    finally:
        flow.close()


def test_expiry_and_safe_exchange_failure(monkeypatch):
    flow = auth.Flow(headless=True)
    flow.deadline = 0
    with pytest.raises(MlcaUserError):
        flow.accept("code")
    flow = auth.Flow(headless=True)
    flow.accept("secret-code")

    def fail(*args, **kwargs):
        raise ValueError("secret-code secret-verifier")

    monkeypatch.setattr(auth.urllib.request, "urlopen", fail)
    with pytest.raises(MlcaUserError) as exc:
        flow.exchange()
    assert "secret-code" not in str(exc.value)


def test_reject_plaintext_backend(monkeypatch):
    import keyring

    monkeypatch.setattr(keyring, "get_keyring", lambda: object())
    with pytest.raises(MlcaUserError, match="Secure OS keyring"):
        auth.secure_backend()
    ref = auth.store_key("canary", persistent=False)
    assert credentials.resolve(ref) == "canary"


def test_keyring_resolve_redact_and_signout(monkeypatch):
    class Backend:
        value = None

        def set_password(self, *args):
            self.value = args[-1]

        def get_password(self, *args):
            return self.value

        def delete_password(self, *args):
            self.value = None

    backend = Backend()
    monkeypatch.setattr(auth, "secure_backend", lambda: backend)
    assert auth.store_key("persistent-canary") == auth.REFERENCE
    credentials.forget()
    assert credentials.resolve(auth.REFERENCE) == "persistent-canary"
    assert redact("persistent-canary") == "[REDACTED]"
    auth.signout()
    assert credentials.resolve(auth.REFERENCE) is None


def test_storage_failure_has_no_plaintext_fallback(monkeypatch, tmp_path):
    def broken():
        raise RuntimeError("backend-secret")

    monkeypatch.setattr(auth, "secure_backend", broken)
    before = set(tmp_path.rglob("*"))
    with pytest.raises(MlcaUserError) as exc:
        auth.store_key("canary")
    assert "backend-secret" not in str(exc.value)
    assert set(tmp_path.rglob("*")) == before


def test_free_configuration_preserves_optional_roles(monkeypatch):
    monkeypatch.setattr("mlca.llm.catalog.save_prices", lambda *args: None)
    config = Config(
        providers={"old": ProviderConfig(kind="fake")},
        roles={
            "inspector": RoleConfig(provider="old", model="old"),
            "worker": RoleConfig(provider="old", model="old", max_output_tokens=8192),
        },
    )
    updated = auth.configure_free(config, auth.REFERENCE)
    assert updated.roles["worker"].max_output_tokens == 8192
    assert updated.roles["inspector"].model == "old"
    assert updated.roles["navigator"].model == "openrouter/free"
    assert updated.providers["openrouter_free"].request_cost_bound_usd is None
    assert updated.providers["openrouter_free"].structured_outputs is None
    assert "canary" not in updated.model_dump_json()


def test_signed_credential_cannot_be_sent_to_other_endpoint():
    from mlca.llm.providers.openai_compatible import CompatibleProvider

    with pytest.raises(MlcaUserError, match="only be used at OpenRouter"):
        CompatibleProvider(
            ProviderConfig(
                kind="openai_compatible", base_url="https://example.com/v1", api_key_env=auth.REFERENCE
            )
        )


def test_cli_headless_signin_and_config_canary(monkeypatch, tmp_path):
    from typer.testing import CliRunner

    from mlca.cli.main import app
    from mlca.config import load

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    monkeypatch.setattr(auth, "secure_backend", lambda: object())
    monkeypatch.setattr(auth, "store_key", lambda key: auth.REFERENCE)
    monkeypatch.setattr(
        auth.urllib.request, "urlopen", lambda *args, **kwargs: io.BytesIO(b'{"key":"cli-key-canary"}')
    )
    result = CliRunner().invoke(app, ["signin", "--headless"], input="authorization-canary\n")
    assert result.exit_code == 0, result.output
    assert "cli-key-canary" not in result.output
    assert "authorization-canary" not in result.output
    assert load().roles["worker"].model == "openrouter/free"
    for file in tmp_path.rglob("*"):
        if file.is_file():
            assert b"cli-key-canary" not in file.read_bytes()


def test_http_callback_and_invalid_request(monkeypatch):
    import threading
    import urllib.error

    flow = auth.Flow()
    thread = threading.Thread(target=flow.wait)
    thread.start()
    base = f"http://127.0.0.1:{flow.server.server_port}/callback"
    try:
        with pytest.raises(urllib.error.HTTPError):
            urllib.request.urlopen(base + "?state=bad&code=bad")
        with urllib.request.urlopen(base + f"?state={flow.state}&code=accepted") as response:
            assert response.status == 200
            assert response.headers["Cache-Control"] == "no-store"
        thread.join(timeout=2)
        assert not thread.is_alive()
        assert flow.code == "accepted"
    finally:
        flow.close()


def test_session_signout_removes_only_that_key():
    reference = credentials.remember("session-key")
    other = credentials.remember("other-provider-key")
    credentials.forget_reference(reference)
    assert credentials.resolve(reference) is None
    assert credentials.resolve(other) == "other-provider-key"
