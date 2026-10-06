import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from mlca.cli.main import app
from mlca.errors import MlcaUserError
from mlca.mcp.install import client_status, install, registration


@pytest.fixture
def client_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: home))
    for variable, value in {
        "CODEX_HOME": home / ".codex",
        "CLAUDE_CONFIG_DIR": home / ".claude",
        "HERMES_HOME": home / ".hermes",
        "OPENCLAW_CONFIG_PATH": home / ".openclaw/openclaw.json",
    }.items():
        monkeypatch.setenv(variable, str(value))
    return home


def test_registration_previews_never_execute(client_home, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("mlca.mcp.install.subprocess.run", lambda *a, **k: calls.append(a))
    monkeypatch.setattr("mlca.mcp.install.shutil.which", lambda name: name)
    runner = CliRunner()
    for client in ("claude", "codex", "hermes", "openclaw", "cursor", "json"):
        result = runner.invoke(app, ["mcp", "install", "--client", client])
        assert result.exit_code == 0, result.output
        assert "mlca" in result.output and "brain" in result.output
        if client in {"json", "cursor"}:
            assert json.loads(result.output)["mcpServers"]["mlca"]["args"] == ["mcp", "--mode", "brain"]
    assert calls == [] and list(client_home.iterdir()) == []
    command = registration("claude", "project", "driver", tmp_path)["command"]
    assert command[:6] == ["claude", "mcp", "add", "--scope", "project", "mlca"]
    assert command[-2:] == ["--project", str(tmp_path)]
    for client in ("codex", "hermes", "openclaw"):
        with pytest.raises(MlcaUserError, match="user scope"):
            registration(client, "project")


@pytest.mark.skipif(os.name == "nt", reason="POSIX fake executable; argv mocking covers Windows")
def test_fake_clients_yes_and_backups(client_home, tmp_path, monkeypatch):
    folder = tmp_path / "bin"
    folder.mkdir()
    record = tmp_path / "calls.jsonl"
    for client in ("claude", "codex", "hermes", "openclaw"):
        file = folder / client
        file.write_text(
            f"#!{sys.executable}\nimport json, sys\n"
            f"with open({str(record)!r}, 'a') as f: f.write(json.dumps(sys.argv) + '\\n')\n"
        )
        file.chmod(0o700)
    monkeypatch.setenv("PATH", str(folder))
    for client in ("claude", "codex", "hermes", "openclaw"):
        config = registration(client)["config"]
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text("CANARY_OLD_CLIENT_CONFIG")
        before = record.read_text() if record.exists() else ""
        preview = install(client, project=tmp_path)
        assert preview.startswith(client + " ")
        assert (record.read_text() if record.exists() else "") == before
        install(client, project=tmp_path, yes=True, with_skill=client != "openclaw")
        saved = list(config.parent.glob(config.name + ".mlca-backup-*"))
        assert len(saved) == 1 and saved[0].read_text() == "CANARY_OLD_CLIENT_CONFIG"
        assert not saved[0].stat().st_mode & 0o077
    lines = [json.loads(line) for line in record.read_text().splitlines()]
    assert len(lines) == 4
    assert lines[0][1:7] == ["mcp", "add", "--scope", "user", "mlca", "--"]
    assert lines[1][1:5] == ["mcp", "add", "mlca", "--"]
    assert lines[2][1:6] == ["mcp", "add", "mlca", "--command", "mlca"]
    assert json.loads(lines[3][-1])["args"] == ["mcp", "--mode", "brain"]
    assert all(
        (client_home / folder / "skills/mlca/SKILL.md").exists()
        for folder in (".claude", ".codex", ".hermes")
    )


def test_cursor_merge_skill_and_errors(client_home, tmp_path, monkeypatch):
    config = client_home / ".cursor/mcp.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"other": 1, "mcpServers": {"existing": {"command": "example"}}}))
    monkeypatch.setattr("mlca.mcp.install.subprocess.run", lambda *a, **k: pytest.fail("Executed"))
    install("cursor", yes=True, project=tmp_path)
    saved = json.loads(config.read_text())
    assert saved["other"] == 1 and "existing" in saved["mcpServers"] and "mlca" in saved["mcpServers"]
    assert list(config.parent.glob("mcp.json.mlca-backup-*"))
    config.write_text("invalid")
    with pytest.raises(MlcaUserError, match="invalid"):
        install("cursor", yes=True, project=tmp_path)
    assert config.read_text() == "invalid"
    with pytest.raises(MlcaUserError, match="skill copying"):
        install("cursor", yes=True, with_skill=True, project=tmp_path)


def test_doctor_registration_status_no_config_output(monkeypatch):
    monkeypatch.setattr("mlca.mcp.install.shutil.which", lambda name: name if name != "openclaw" else None)
    monkeypatch.setattr(
        "mlca.mcp.install.subprocess.run", lambda *a, **k: SimpleNamespace(stdout="mlca SECRET")
    )
    result = client_status()
    assert result["claude"]["registration"] == "listed"
    assert not result["openclaw"]["available"]
    assert "SECRET" not in json.dumps(result)


def test_yes_uses_argv_without_shell(client_home, tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("mlca.mcp.install.shutil.which", lambda name: name)
    monkeypatch.setattr("mlca.mcp.install.subprocess.run", lambda *a, **k: calls.append((a, k)))
    install("claude", scope="project", mode="driver", project=tmp_path, yes=True)
    assert calls[0][0][0] == registration("claude", "project", "driver", tmp_path)["command"]
    assert "shell" not in calls[0][1] and calls[0][1]["cwd"] == tmp_path
