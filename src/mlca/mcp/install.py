"""Preview registrations; change client configuration only with explicit --yes."""

import json
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

from ulid import ULID

from mlca.errors import MlcaUserError
from mlca.paths import atomic_json, resource

CLIENTS = {"claude", "codex", "hermes", "openclaw", "cursor", "json"}


def registration(client, scope="user", mode="brain", project=None):
    if client not in CLIENTS or scope not in {"user", "project"} or mode not in {"brain", "driver"}:
        raise MlcaUserError("Choose a supported client, user/project scope and brain/driver mode")
    if scope == "project" and client in {"codex", "hermes", "openclaw"}:
        raise MlcaUserError(f"{client} registration supports user scope here; use --scope user")
    home = Path.home()
    project = Path(project or Path.cwd()).resolve()
    entry = {"command": shutil.which("mlca") or "mlca", "args": ["mcp", "--mode", mode]}
    if scope == "project":
        entry["args"] += ["--project", str(project)]
    result = {"client": client, "entry": entry, "command": None, "config": None}
    if client == "claude":
        result["command"] = [
            "claude",
            "mcp",
            "add",
            "--scope",
            scope,
            "mlca",
            "--",
            entry["command"],
            *entry["args"],
        ]
        user_config = (
            Path(os.environ["CLAUDE_CONFIG_DIR"]) / ".claude.json"
            if os.environ.get("CLAUDE_CONFIG_DIR")
            else home / ".claude.json"
        )
        result["config"] = project / ".mcp.json" if scope == "project" else user_config
    elif client == "codex":
        result["command"] = ["codex", "mcp", "add", "mlca", "--", entry["command"], *entry["args"]]
        result["config"] = Path(os.environ.get("CODEX_HOME", home / ".codex")) / "config.toml"
    elif client == "hermes":
        result["command"] = [
            "hermes",
            "mcp",
            "add",
            "mlca",
            "--command",
            entry["command"],
            "--args",
            *entry["args"],
        ]
        result["config"] = Path(os.environ.get("HERMES_HOME", home / ".hermes")) / "config.yaml"
    elif client == "openclaw":
        result["command"] = ["openclaw", "mcp", "set", "mlca", json.dumps(entry)]
        result["config"] = Path(os.environ.get("OPENCLAW_CONFIG_PATH", home / ".openclaw/openclaw.json"))
    elif client == "cursor":
        result["config"] = (project if scope == "project" else home) / ".cursor/mcp.json"
    return result


def backup(path):
    if path.is_symlink():
        raise MlcaUserError("Refusing to replace or back up a symlinked configuration")
    if path.is_file():
        destination = path.with_name(path.name + ".mlca-backup-" + str(ULID()))
        destination.touch(mode=0o600, exist_ok=False)
        shutil.copyfile(path, destination)
        destination.chmod(0o600)
        return destination
    return None


def skill_target(client, scope, project):
    home = Path.home()
    if client == "claude":
        parent = (
            Path(project) / ".claude"
            if scope == "project"
            else Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
        )
    elif client == "codex":
        parent = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    elif client == "hermes":
        parent = Path(os.environ.get("HERMES_HOME", home / ".hermes"))
    else:
        raise MlcaUserError("Automatic skill copying supports claude, codex and hermes only")
    return parent / "skills/mlca/SKILL.md"


def install(client, scope="user", mode="brain", project=None, yes=False, with_skill=False):
    project = Path(project or Path.cwd()).resolve()
    plan = registration(client, scope, mode, project)
    target = skill_target(client, scope, project) if with_skill else None
    if plan["command"]:
        preview = subprocess.list2cmdline(plan["command"]) if os.name == "nt" else shlex.join(plan["command"])
    else:
        preview = json.dumps({"mcpServers": {"mlca": plan["entry"]}}, indent=2)
    if target:
        preview += f"\nSkill: {target}"
    if not yes or client == "json":
        return preview
    if plan["command"] and not shutil.which(client):
        raise MlcaUserError(f"{client} is not on PATH; registration was not performed")
    if target and (target.is_symlink() or any(p.is_symlink() for p in target.parents)):
        raise MlcaUserError("Refusing a symlinked skill destination")
    config = plan["config"]
    backup(config)
    if plan["command"]:
        try:
            subprocess.run(plan["command"], cwd=project, check=True, capture_output=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            raise MlcaUserError("Client registration failed; restore its backup if needed") from None
    else:
        try:
            saved = json.loads(config.read_text(encoding="utf-8")) if config.exists() else {}
            if not isinstance(saved, dict) or not isinstance(saved.get("mcpServers", {}), dict):
                raise ValueError()
            saved.setdefault("mcpServers", {})["mlca"] = plan["entry"]
        except (ValueError, OSError):
            raise MlcaUserError("Client JSON configuration is invalid; no replacement written") from None
        atomic_json(config, saved)
        config.chmod(0o600)
    if target:
        target.parent.mkdir(parents=True, exist_ok=True)
        backup(target)
        shutil.copyfile(resource("skills") / "mlca/SKILL.md", target)
    return preview + "\nRegistered. Restart the client and check its MCP tool list."


def client_status():
    """Query client list commands, returning presence only, never config contents."""
    result = {}
    for client in ("claude", "codex", "hermes", "openclaw"):
        if not shutil.which(client):
            result[client] = {"available": False, "registration": "not checked"}
            continue
        try:
            completed = subprocess.run(
                [client, "mcp", "list"], capture_output=True, text=True, timeout=5, check=True
            )
            found = bool(re.search(r"(?<![\w-])mlca(?![\w-])", completed.stdout))
            result[client] = {"available": True, "registration": "listed" if found else "not listed"}
        except (OSError, subprocess.SubprocessError):
            result[client] = {"available": True, "registration": "unavailable or timed out"}
    result["cursor"] = {"registration": "check Cursor MCP settings manually"}
    return result
