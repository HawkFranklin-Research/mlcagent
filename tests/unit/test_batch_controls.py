from mlca.config import Config, ProviderConfig
from mlca.llm.client import Client, RequestContext, pace
from mlca.rails import load, snapshot


def test_rate_state_shared_despite_isolated_config_directories(tmp_path, monkeypatch):
    config = ProviderConfig(kind="openrouter", requests_per_minute=1, rate_limit_dir=str(tmp_path / "shared"))
    now = [1000.0]

    def sleep(seconds):
        now[0] += seconds

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "first"))
    assert pace(config, "configured/model", now=lambda: now[0], sleep=sleep) == 0
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "second"))
    assert pace(config, "configured/model", now=lambda: now[0], sleep=sleep) == 60


def test_unlimited_is_explicit_and_defaults_remain_limited(tmp_path):
    assert Config().budgets.turn_max_usd == 1
    config = Config.model_validate({"budgets": {"turn_max_usd": None, "session_max_usd": None}})
    client = Client(tmp_path, config)
    provider = ProviderConfig(kind="openrouter")
    client._budget(
        {},
        type("Role", (), {"provider": "configured", "model": "configured/model", "max_output_tokens": 100})(),
        provider,
        RequestContext(role="worker", session_id="fixture"),
    )


def test_ablation_is_a_project_snapshot_not_a_global_edit(tmp_path):
    from mlca.paths import resource

    before = load(resource("rails")).sha256
    details = snapshot(tmp_path / "disabled", enabled=False)
    assert details["version"] == "rails-0.0"
    assert not list((tmp_path / "disabled").glob("*.yaml"))
    assert load(resource("rails")).sha256 == before
