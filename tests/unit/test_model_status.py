from mlca.config import Config, ProviderConfig, RoleConfig
from mlca.llm.status import roles


def test_status_health_and_actual_model(monkeypatch):
    config = Config(
        providers={"local": ProviderConfig(kind="openai_compatible")},
        roles={"worker": RoleConfig(provider="local", model="requested")},
    )
    assert roles(config, [])["worker"]["health"] == "grey"
    entry = {
        "role": "worker",
        "provider": "local",
        "model": "requested",
        "status": "ok",
        "model_reported": "actual",
        "latency_ms": 10,
    }
    assert roles(config, [entry])["worker"]["health"] == "green"
    assert roles(config, [entry])["worker"]["model_reported"] == "actual"
    assert roles(config, [{**entry, "status": "error", "status_code": 429}])["worker"]["health"] == "yellow"
    assert roles(config, [{**entry, "status": "error"}])["worker"]["health"] == "red"
    assert roles(config, [entry])["worker"]["quota_limit"] is None


def test_explicit_connection_test_makes_one_attempt(monkeypatch, tmp_path):
    import yaml

    from mlca.llm.connection import test_connection as check
    from mlca.llm.usage import read

    script = tmp_path / "fake.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "responses": [
                    {"match": {"purpose": "connection_test"}, "text": "OK", "model_reported": "fake-actual"}
                ]
            }
        )
    )
    config = Config(
        providers={"test": ProviderConfig(kind="fake", script=str(script))},
        roles={"worker": RoleConfig(provider="test", model="requested")},
    )
    (tmp_path / ".mlca").mkdir()
    result = check(config, tmp_path, "worker")
    assert result["model_reported"] == "fake-actual"
    assert len(read(tmp_path)) == 1
    assert read(tmp_path)[0]["purpose"] == "connection_test"


def test_generic_keyring_reference_redaction(monkeypatch):
    from mlca.config import redact
    from mlca.llm import credentials, openrouter_auth

    class Backend:
        values = {}

        def set_password(self, service, name, value):
            self.values[name] = value

        def get_password(self, service, name):
            return self.values.get(name)

    monkeypatch.setattr(openrouter_auth, "secure_backend", lambda: Backend())
    reference = credentials.remember_secure("api-key-canary", "provider")
    credentials.forget()
    assert credentials.resolve(reference) == "api-key-canary"
    assert redact("api-key-canary") == "[REDACTED]"
    credentials.forget()
