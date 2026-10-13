"""Transient client presence, not evidence or authorization. Never contains credentials."""

import json
import os
import time

from mlca.paths import atomic_json


def register(session):
    atomic_json(
        session.root / ".mlca/live-clients" / (session.session_id + ".json"),
        {
            "session_id": session.session_id,
            "actor": session.principal,
            "mode": session.mode,
            "pid": os.getpid(),
            "updated_at": time.time(),
        },
    )


def unregister(session):
    (session.root / ".mlca/live-clients" / (session.session_id + ".json")).unlink(missing_ok=True)


def clients(session):
    values = []
    for path in (session.root / ".mlca/live-clients").glob("*.json"):
        if path.is_symlink():
            continue
        try:
            value = json.loads(path.read_text())
            if value["session_id"] == session.session_id or value["mode"] not in {"brain", "driver"}:
                continue
            os.kill(value["pid"], 0)
            values.append(value)
        except (OSError, ValueError, KeyError, TypeError):
            continue
    return sorted(values, key=lambda v: v.get("updated_at", 0))


def project_busy(session):
    from filelock import FileLock, Timeout

    try:
        with FileLock(str(session.root / ".mlca/action.lock"), timeout=0):
            return False
    except Timeout:
        return True
