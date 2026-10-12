import io
import json

from mlca.config import Config, ProviderConfig
from mlca.llm.credentials import remember
from mlca.llm.quota import for_provider, refresh


def test_provider_quota_is_explicit_and_secret_free(tmp_path, monkeypatch):
    (tmp_path / ".mlca").mkdir()
    (tmp_path / ".mlca/project.yaml").write_text("project")
    reference = remember("quota-key-canary")
    provider = ProviderConfig(kind="openrouter", api_key_env=reference)
    config = Config(providers={"router": provider})
    body = {"data": {"free_model_daily_requests": {"used": 12, "limit": 50}, "ignored": "quota-key-canary"}}
    monkeypatch.setattr(
        "mlca.llm.quota.urllib.request.urlopen", lambda *args, **kwargs: io.BytesIO(json.dumps(body).encode())
    )
    assert refresh(tmp_path, config)["router"]["used"] == 12
    assert for_provider(tmp_path, "router", provider)["limit"] == 50
    assert "quota-key-canary" not in (tmp_path / ".mlca/provider-quota.json").read_text()
    changed = ProviderConfig(kind="openrouter", api_key_env=remember("another-key"))
    assert for_provider(tmp_path, "router", changed) == {}
    body["data"]["free_model_daily_requests"] = {}
    assert refresh(tmp_path, config)["router"]["used"] is None
