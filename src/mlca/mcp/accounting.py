"""One committed envelope per dispatched MCP result, without storing its content."""

import hashlib
import time
from datetime import datetime, timezone

from ulid import ULID

from mlca.llm.usage import persist
from mlca.paths import canonical


def categories(tool, arguments, response):
    if any(c.type == "image" for c in response.content):
        return ["figure_image"]
    if tool in {"mlca_options", "mlca_submit_options", "mlca_choose", "mlca_custom", "mlca_step_status"}:
        return ["template_spec", "facts"]
    if tool == "mlca_read":
        return [
            {
                "script": "script",
                "table": "table_summary",
                "log": "inventory_summary",
                "facts": "facts",
                "report": "inventory_summary",
            }.get(arguments.get("kind"), "inventory_summary")
        ]
    if response.is_error:
        return ["traceback"]
    return ["inventory_summary", "facts"]


def record(root, session, tool, arguments, actor, response, started, notifications=None):
    request_id = str(ULID())
    payload = canonical(response.model_dump(mode="json", by_alias=True, exclude_none=True)).encode()
    ts = datetime.now(timezone.utc).isoformat()
    elapsed = time.monotonic() - started
    sid = session.session_id if session else "mcp-unopened"
    entry = {
        "request_id": request_id,
        "role": "mcp",
        "principal": actor,
        "tool": tool,
        "ts": ts,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "categories": categories(tool, arguments, response),
    }
    usage = {
        "request_id": request_id,
        "role": "mcp",
        "principal": actor,
        "tool": tool,
        "ts": ts,
        "session_id": sid,
        "event_id": session.state.current_event if session else None,
        "step_id": arguments.get("step_id")
        or (response.structured_content or {}).get("data", {}).get("step_id"),
        "duration_s": elapsed,
        "latency_ms": elapsed * 1000,
        "cost_source": "external",
        "cost_usd": None,
        "reserved_cost_usd": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cached_tokens": 0,
        "status": "refused" if response.is_error else "ok",
        "category": (response.structured_content or {}).get("data", {}).get("category")
        if response.is_error
        else None,
    }
    (root / ".mlca").mkdir(parents=True, exist_ok=True)
    encoded_notifications = canonical(notifications or []).encode()
    entry["progress_metadata_bytes"] = len(encoded_notifications) if notifications else 0
    entry["progress_metadata_sha256"] = hashlib.sha256(encoded_notifications).hexdigest()
    entry["progress_delivery"] = "client-dependent"
    persist(root, usage, entry)
