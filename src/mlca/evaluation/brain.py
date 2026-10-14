"""Isolated headless MCP clients; MLCA's model client is never used in brain mode."""

import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

from mlca.api import Session
from mlca.config import redact
from mlca.errors import MlcaUserError
from mlca.llm.usage import persist
from mlca.paths import atomic_json, canonical

CLIENTS = {"claude", "codex", "opencode"}


def prompt_text(card, root):
    from mlca.evaluation.bio_bench import instructions

    return (
        "\n".join(
            [
                "Complete this study using only the MLCA MCP tools. MLCA makes no model calls.",
                "Project: " + str(root),
                "Template: " + card.template,
                "Study brief: " + canonical(card.brief),
                "Ordered custom instructions (issue each once in its event; retain refusals): "
                + canonical(instructions(card)),
                "Use mlca_open, mlca_status and mlca_options; propose validated options and submit scripts as requested.",
                "Request human-only decisions through approvals; the separate task-card policy resolves only declared approvals.",
                "Poll long steps. Never read data or key files, use a shell, approve your own requests, change the protocol after test exposure, or replace failed Worker code.",
                "Stop at completed report or an unrecoverable failure and explain the category.",
            ]
        )
        + "\n"
    )


def client_plan(client, model, root, directory):
    if client not in CLIENTS or not model:
        raise MlcaUserError(
            "Choose opencode, claude or codex and an explicit model", category="invalid_request"
        )
    root, directory = Path(root), Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    entry = {
        "command": sys.executable,
        "args": ["-m", "mlca", "mcp", "--mode", "brain", "--project", str(root)],
    }
    env = {
        "OPENCODE_CONFIG_PROJECT_DISABLE": "1",
        "CLAUDE_CONFIG_DIR": str(directory / "claude"),
        "CODEX_HOME": str(directory / "codex"),
        "OPENCODE_CONFIG_DIR": str(directory / "opencode"),
    }
    for name, path in env.items():
        if not name.endswith(("DIR", "HOME")):
            continue
        Path(path).mkdir(parents=True, exist_ok=True)
    if client == "claude":
        path = directory / "mcp.json"
        atomic_json(path, {"mcpServers": {"mlca": entry}})
        command = [
            "claude",
            "-p",
            "--output-format",
            "json",
            "--strict-mcp-config",
            "--mcp-config",
            str(path),
            "--tools",
            "",
            "--allowedTools",
            "mcp__mlca__*",
            "--setting-sources",
            "",
            "--model",
            model,
        ]
    elif client == "codex":
        path = Path(env["CODEX_HOME"]) / "config.toml"
        path.write_text(
            'approval_policy = "never"\nsandbox_mode = "read-only"\nweb_search = "disabled"\n[features]\nshell_tool = false\nskill_mcp_dependency_install = false\n[mcp_servers.mlca]\ncommand = '
            + json.dumps(entry["command"])
            + "\nargs = "
            + json.dumps(entry["args"])
            + "\n"
        )
        command = [
            "codex",
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--sandbox",
            "read-only",
            "--model",
            model,
            "-",
        ]
    else:
        path = Path(env["OPENCODE_CONFIG_DIR"]) / "opencode.json"
        atomic_json(
            path,
            {
                "mcp": {
                    "mlca": {
                        "type": "local",
                        "command": [entry["command"], *entry["args"]],
                        "codemode": False,
                    }
                },
                "permissions": [
                    {"action": "*", "resource": "*", "effect": "deny"},
                    {"action": "mlca_*", "resource": "*", "effect": "allow"},
                ],
                "update": "disable",
                "share": "disabled",
            },
        )
        # Server logs go to brain_stderr.txt: they show MCP discovery and whether tools reached the model.
        command = ["opencode", "run", "--standalone", "--print-logs", "--format", "json", "--model", model]
    if client == "opencode":
        env["OPENCODE_CONFIG"] = str(path)
    return {"command": command, "env": env, "config": str(path), "client": client, "model": model}


def policy_once(session, policy):
    """The agent requests; the separately attributed policy decides only declared kinds."""
    resolved = []
    for request in session.approvals():
        allowed = (
            (request["kind"] == "confirm" and policy.confirm_subgoals)
            or (request["kind"] == "unlock_test" and policy.unlock_test)
            or (request["kind"] == "package" and request["target"] in policy.packages)
        )
        if allowed:
            session.resolve_approval(
                request["request_id"],
                "approved",
                policy.note,
                phrase="UNLOCK TEST" if request["kind"] == "unlock_test" else "",
            )
            resolved.append(request["request_id"])
    for q in session.questions():
        session.answer_question(q["question_id"], q["recommended"])
    return resolved


def parse_output(text, client, model=None):
    """Whitelisted numeric fields only. Absent counts and monetary costs stay unavailable."""
    from mlca.evaluation.import_usage import number

    try:
        obj = json.loads(text)
        rows = obj if isinstance(obj, list) else [obj]
    except ValueError:
        rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        if client == "claude" and row.get("type") == "result":
            u = row.get("usage") or {}
            counts = {
                "input_tokens": u.get("input_tokens"),
                "output_tokens": u.get("output_tokens"),
                "cached_tokens": u.get("cache_read_input_tokens"),
                "cache_write_tokens": u.get("cache_creation_input_tokens"),
                "reasoning_tokens": u.get("reasoning_tokens"),
                "cost_usd": row.get("total_cost_usd"),
            }
        elif client == "codex" and row.get("type") == "turn.completed":
            u = row.get("usage") or {}
            counts = {
                "input_tokens": u.get("input_tokens"),
                "output_tokens": u.get("output_tokens"),
                "cached_tokens": u.get("cached_input_tokens"),
                "reasoning_tokens": u.get("reasoning_output_tokens"),
                "cost_usd": u.get("cost_usd"),
            }
        elif client == "opencode" and row.get("type") == "step_finish":
            part = row.get("part") or {}
            u = part.get("tokens") or {}
            cache = u.get("cache") or {}
            counts = {
                "input_tokens": u.get("input"),
                "output_tokens": u.get("output"),
                "reasoning_tokens": u.get("reasoning"),
                "cached_tokens": cache.get("read"),
                "cache_write_tokens": cache.get("write"),
                "cost_usd": part.get("cost"),
            }
        else:
            continue
        yield {
            "message_id": str((row.get("part") or {}).get("id") or index),
            "model": model,
            "model_reported": row.get("model"),
            **{k: number(v) for k, v in counts.items()},
        }


def capture_usage(session, path, client, model):
    count = 0
    for row in parse_output(Path(path).read_text(), client, model):
        digest = hashlib.sha256(canonical([client, row, Path(path).name]).encode()).hexdigest()
        record = {
            "request_id": "external-" + digest,
            "role": "external_agent",
            "provider": client,
            "session_id": "external:" + session.state.project_id,
            "principal": "agent:" + client + "/client-reported",
            "import_branch": session.branch_name,
            "status": "ok",
            "source": "client-reported",
            "cost_source": "client",
            "reserved_cost_usd": 0.0,
            "latency_ms": None,
            "ts": datetime.now(timezone.utc).isoformat(),
            **row,
        }
        persist(session.root, record, {"request_id": record["request_id"], "imported": True})
        count += 1
    return count


def run(session, card, client, model, timeout_s=1800):
    root = session.root
    directory = root / ".mlca/private/brain-client"
    plan = client_plan(client, model, root, directory)
    executable = shutil.which(client)
    if executable is None:
        raise MlcaUserError(client + " is not installed", category="invalid_request")
    help_args = (
        [executable, "exec", "--help"]
        if client == "codex"
        else [executable, "run", "--help"]
        if client == "opencode"
        else [executable, "--help"]
    )
    help_text = subprocess.run(help_args, capture_output=True, text=True, check=True, timeout=15).stdout
    flags = [arg for arg in plan["command"][1:] if arg.startswith("--")]
    if any(flag not in help_text for flag in flags):
        raise MlcaUserError(
            "Installed client does not support required isolated-run flags", category="invalid_request"
        )
    prompt = prompt_text(card, root)
    (root / "brain_prompt.md").write_text(prompt)
    stop, errors = threading.Event(), []

    def approve():
        with Session.open(
            root, client="brain-policy", principal=session.principal, policy=True, mode="brain"
        ) as s:
            while not stop.wait(0.2):
                try:
                    policy_once(s, card.approval_policy)
                except MlcaUserError:
                    pass  # Busy/stale requests remain pending rather than bypassing the engine.
                except Exception as error:
                    errors.append(type(error).__name__)
                    stop.set()

    thread = threading.Thread(target=approve, daemon=True)
    thread.start()
    command = [executable, *plan["command"][1:]]
    if client == "opencode":
        command.append(prompt)
    env = {**os.environ, **plan["env"]}
    if client == "opencode":
        from mlca.llm.credentials import resolve

        provider = next((p for p in session.config.providers.values() if p.kind == "openrouter"), None)
        if provider and provider.api_key_env:
            key = resolve(provider.api_key_env)
            if key:
                env["OPENROUTER_API_KEY"] = key
        if not model.startswith("openrouter/"):
            command[command.index("--model") + 1] = "openrouter/" + model
    plan["command"] = command[:-1] if client == "opencode" else command
    process = subprocess.Popen(
        command,
        cwd=directory,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=os.name == "posix",
    )
    category = None
    try:
        stdout, stderr = process.communicate(None if client == "opencode" else prompt, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        stdout, stderr = process.communicate()
        category = "timeout"
    finally:
        stop.set()
        thread.join(timeout=5)
    stdout, stderr = redact(stdout, session.config), redact(stderr, session.config)
    raw = root / "brain_output.jsonl"
    raw.write_text(stdout)
    (root / "brain_stderr.txt").write_text(stderr)
    atomic_json(root / "brain_client.json", {k: v for k, v in plan.items() if k != "env"})
    try:
        capture_usage(session, raw, client, model)
    except (ValueError, MlcaUserError):
        session.emit("Note", {"text": "Client usage unavailable: malformed output"})
    if category or errors or process.returncode or session.state.event_statuses.get("report") != "done":
        raise MlcaUserError(
            "Brain client did not complete; raw output and failed run retained",
            category=category or "client_failure",
        )
    return plan
