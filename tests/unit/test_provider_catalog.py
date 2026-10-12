import json

import pytest

from mlca.config import Config, ProviderConfig, redact, save
from mlca.llm.catalog import cached, fetch, parse, save_prices
from mlca.llm.credentials import forget, remember, resolve
from mlca.llm.pricing import estimate


def test_session_keys_never_serialized(tmp_path):
    key = "distinctive-session-credential-canary"
    name = remember(key)
    config = Config(providers={"router": ProviderConfig(kind="openrouter", api_key_env=name)})
    path = save(config)
    assert key not in path.read_text()
    assert resolve(name) == key
    assert redact("value=" + key, config) == "value=[REDACTED]"
    forget()
    assert resolve(name) is None


def test_catalog_prices_and_free():
    models = parse(
        {
            "data": [
                {"id": "free", "pricing": {"prompt": "0", "completion": "0"}},
                {"id": "paid", "pricing": {"prompt": "0.000001", "completion": "0.000002"}},
                {"id": "unknown"},
                {"id": "fee", "pricing": {"prompt": "0", "completion": "0", "request": "0.1"}},
                {"id": "invalid", "pricing": {"prompt": "nan", "completion": "-1"}},
            ]
        }
    )
    found = {m.id: m for m in models}
    assert found["free"].free
    assert not found["fee"].free and found["fee"].input_per_million is None
    assert found["paid"].input_per_million == 1
    assert found["unknown"].input_per_million is None
    assert found["invalid"].input_per_million is None
    save_prices("router", models)
    assert estimate("router", "free", 1000, 1000) == 0
    assert estimate("router", "paid", 1000, 1000) == 0.003
    assert estimate("router", "unknown", 1000, 1000) is None


def test_fetch_cache_and_canary(monkeypatch):
    key = "catalog-credential-canary"
    name = remember(key)
    provider = ProviderConfig(kind="openrouter", api_key_env=name)

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self, size):
            return json.dumps(
                {
                    "data": [
                        {
                            "id": "fake/model",
                            "name": key,
                            "private": key,
                            "pricing": {"prompt": "0", "completion": "0"},
                        }
                    ]
                }
            ).encode()

    def request(req, timeout):
        assert req.full_url == "https://openrouter.ai/api/v1/models"
        assert req.get_header("Authorization") == "Bearer " + key
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", request)
    assert fetch(provider)[0].id == "fake/model"
    from mlca.llm.catalog import cache_path

    assert key not in cache_path(provider).read_text()
    assert cached(provider)[1] is False
    forget()


def test_failure_message_does_not_expose_key(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("secret-error-canary")

    monkeypatch.setattr("urllib.request.urlopen", fail)
    with pytest.raises(Exception) as error:
        fetch(ProviderConfig(kind="openrouter"))
    assert "secret-error-canary" not in str(error.value)


def test_session_keys_do_not_enter_analysis_environment(tmp_path, monkeypatch):
    from pathlib import Path

    from mlca.llm.credentials import forget, remember
    from mlca.runner.process import execute

    key = "child-environment-canary"
    name = remember(key)
    captured = {}

    class Stop(Exception):
        pass

    def process(args, **kwargs):
        captured.update(kwargs["env"])
        raise Stop()

    monkeypatch.setattr("subprocess.Popen", process)
    step = tmp_path / "step"
    step.mkdir()
    (step / "outputs").mkdir()
    with pytest.raises(Stop):
        execute(Path("/usr/bin/python3"), step, [], tmp_path, tmp_path, tmp_path / "style", "B", 2)
    assert name not in captured
    assert key not in str(captured)
    forget()
