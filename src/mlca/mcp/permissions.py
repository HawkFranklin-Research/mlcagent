"""Recommended client policy; not proof of the supervising agent's file access."""

import json
from pathlib import Path

from mlca.errors import MlcaUserError
from mlca.paths import user_data_dir


def absolute_pattern(path):
    # Claude uses // for filesystem-root paths, including normalized Windows drives.
    value = Path(path).resolve().as_posix()
    if len(value) > 1 and value[1] == ":":
        value = "/" + value[0].lower() + value[2:]
    for character in ("\\", "*", "?", "[", "]"):
        value = value.replace(character, "\\" + character)
    return "/" + value


def claude_block(project):
    project = Path(project).resolve()
    deny = [
        "Read(./.mlca/**)",
        "Edit(./.mlca/**)",
        f"Read({absolute_pattern(project / '.mlca')}/**)",
        f"Edit({absolute_pattern(project / '.mlca')}/**)",
        "Read(~/.local/share/mlca/**)",
        "Edit(~/.local/share/mlca/**)",
        f"Read({absolute_pattern(user_data_dir())}/**)",
        f"Edit({absolute_pattern(user_data_dir())}/**)",
        "Bash(mlca approvals:*)",
        "Bash(mlca unlock-test:*)",
        "Bash(mlca confirm:*)",
        "Bash(mlca package:*)",
        # Prefix rules alone miss -p, absolute executables, Python and shell wrappers.
        "Bash",
        "PowerShell",
        "Edit(./.claude/**)",
    ]
    for folder in ("tables", "figures", "reports", "scripts"):
        deny.extend(
            [
                f"Read({absolute_pattern(project / folder)}/**)",
                f"Edit({absolute_pattern(project / folder)}/**)",
            ]
        )
    if (project / ".mlca/log/events.jsonl").exists():
        from mlca.log.store import Store

        paths = {
            r.payload["original_path"] for r in Store(project).read() if r.type.value == "DataRegistered"
        }
        for path in sorted(paths):
            deny.extend([f"Read({absolute_pattern(path)})", f"Edit({absolute_pattern(path)})"])
    return {
        "permissions": {
            "deny": list(dict.fromkeys(deny)),
            "defaultMode": "default",
            "disableBypassPermissionsMode": "disable",
        }
    }


def guidance(client, project):
    if client == "claude":
        path = Path(project) / ".claude/settings.json"
        return f"Recommended project permissions ({path}):\n" + json.dumps(claude_block(project), indent=2)
    return (
        "Trust boundary: agent file access is unknown (outside MLCA). Disable native file, shell, "
        "execution and other filesystem MCP tools; keep data, .mlca and the MLCA key folder "
        "outside the agent's OS access. Only the human may invoke confirmations, approvals, "
        "test unlocks or package installs. Codex --sandbox read-only limits writes, not reads. "
        "Use an MCP-only client or separate OS identity/container for an enforceable boundary."
    )


def merged_settings(path, block):
    try:
        value = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        if not isinstance(value, dict) or not isinstance(value.get("permissions", {}), dict):
            raise ValueError()
        permission = value.setdefault("permissions", {})
        current = permission.get("deny", [])
        if not isinstance(current, list) or not all(isinstance(rule, str) for rule in current):
            raise ValueError()
        permission.update(block["permissions"])
        permission["deny"] = list(dict.fromkeys(current + block["permissions"]["deny"]))
        return value
    except (ValueError, OSError):
        raise MlcaUserError(
            "Claude project permission settings are invalid; no replacement written"
        ) from None
