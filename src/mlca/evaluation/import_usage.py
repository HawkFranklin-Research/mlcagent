"""Import whitelisted usage fields only; never persist or display transcript content."""

import hashlib
import json
import math
from datetime import datetime
from pathlib import Path

from mlca.config import redact_value
from mlca.errors import MlcaUserError
from mlca.llm.usage import persist
from mlca.paths import canonical


def timestamp(value):
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError
        return result
    except (TypeError, ValueError, AttributeError):
        raise MlcaUserError("Usage timestamps must include a timezone") from None


def number(value):
    return (
        value
        if isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
        and value >= 0
        else None
    )


def resolve(client, reference):
    path = Path(reference).expanduser()
    if path.is_file():
        if path.suffix != ".jsonl":
            raise MlcaUserError("Choose a client session JSONL file")
        return path
    if any(
        c not in "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_" for c in str(reference)
    ):
        raise MlcaUserError("Choose a JSONL path or a session ID")
    base = Path.home() / (".claude/projects" if client == "claude" else ".codex/sessions")
    files = list(base.rglob("*" + str(reference) + ".jsonl"))
    if len(files) != 1:
        raise MlcaUserError("Session ID must resolve to exactly one local JSONL file")
    return files[0]


def extract(path, client):
    model, session_id, previous = None, None, None
    seen = set()
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError
            except ValueError:
                raise MlcaUserError(f"Invalid client JSONL at line {line_number}") from None
            if client == "claude":
                if row.get("type") != "assistant":
                    continue
                message = row.get("message") or {}
                usage = message.get("usage")
                if not isinstance(usage, dict):
                    continue
                model = message.get("model")
                session_id = row.get("sessionId") or path.stem
                ident = message.get("id") or row.get("uuid")
                # Claude streaming can repeat a message ID. The importer replaces the same envelope
                # as usage grows instead of adding another charge.
                counts = {
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "cached_tokens": usage.get("cache_read_input_tokens"),
                    "cache_write_tokens": usage.get("cache_creation_input_tokens"),
                }
                if not ident:
                    continue
            else:
                payload = row.get("payload") or {}
                if row.get("type") == "session_meta":
                    session_id = payload.get("id")
                    continue
                if row.get("type") == "turn_context":
                    model = payload.get("model")
                    continue
                if row.get("type") != "event_msg" or payload.get("type") != "token_count":
                    continue
                info = payload.get("info") or {}
                total = info.get("total_token_usage")
                last = info.get("last_token_usage") or {}
                if not isinstance(total, dict):
                    continue
                total = {
                    k: number(total.get(k))
                    for k in (
                        "input_tokens",
                        "output_tokens",
                        "cached_input_tokens",
                        "cache_write_input_tokens",
                        "reasoning_output_tokens",
                    )
                }
                fingerprint = canonical(total)
                if fingerprint in seen:
                    continue
                seen.add(fingerprint)
                if previous is not None:
                    delta = {
                        k: total[k] - previous[k]
                        if total[k] is not None and previous[k] is not None and total[k] >= previous[k]
                        else last.get(k)
                        for k in total
                    }
                else:
                    delta = last
                previous = total
                ident = hashlib.sha256(fingerprint.encode()).hexdigest()
                session_id = session_id or path.stem
                counts = {
                    "input_tokens": delta.get("input_tokens"),
                    "output_tokens": delta.get("output_tokens"),
                    "cached_tokens": delta.get("cached_input_tokens"),
                    "cache_write_tokens": delta.get("cache_write_input_tokens"),
                    "reasoning_output_tokens": delta.get("reasoning_output_tokens"),
                }
                usage = {}
            if not isinstance(model, str):
                model = None
            yield {
                "ts": row.get("timestamp"),
                "client_session_id": session_id,
                "message_id": ident,
                "model": model,
                "model_reported": model,
                **{k: number(v) for k, v in counts.items()},
                "cost_usd": number(usage.get("cost_usd")),
            }


def import_usage(session, client, reference, since=None, until=None):
    if client not in {"claude", "codex"}:
        raise MlcaUserError("Choose claude or codex")
    records = session.branches.records()
    brain_ids = {
        r.session_id for r in records if r.type.value == "RunSnapshot" and r.payload["mode"] == "brain"
    }
    window = [r.ts for r in records if r.session_id in brain_ids] or [r.ts for r in records]
    lower = max(min(window), timestamp(since)) if since else min(window)
    upper = min(max(window), timestamp(until)) if until else max(window)
    if lower > upper:
        raise MlcaUserError("Import window does not overlap the recorded project run")
    path = resolve(client, reference)
    count = 0
    for row in extract(path, client):
        if row["ts"] is None:
            continue
        ts = timestamp(row["ts"])
        if not lower <= ts <= upper:
            continue
        ident = hashlib.sha256(
            canonical([client, row["client_session_id"], row["message_id"]]).encode()
        ).hexdigest()
        usage = {
            "request_id": "external-" + ident,
            "role": "external_agent",
            "provider": client,
            "principal": "agent:" + client + "/client-reported",
            "session_id": "external:" + str(row["client_session_id"]),
            "import_branch": session.branch_name,
            "cost_source": "client_reported",
            "source": "client-reported",
            "status": "ok",
            "reserved_cost_usd": 0.0,
            "latency_ms": None,
            **row,
        }
        # Do not copy file path, source line, arguments or message content into either ledger.
        persist(
            session.root,
            redact_value(usage, session.config),
            {"request_id": usage["request_id"], "imported": True},
        )
        count += 1
    return {
        "records_processed": count,
        "source": "client-reported",
        "window": {"from": lower.isoformat(), "to": upper.isoformat()},
        "message_text_copied": False,
        "cost_note": "Missing reported cost remains unavailable; subscriptions are not free inference.",
    }
