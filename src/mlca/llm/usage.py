import json
from collections import defaultdict
from pathlib import Path

from filelock import FileLock

from mlca.paths import atomic_json, canonical


def read(root: Path) -> list[dict]:
    folder = root / ".mlca/requests"
    return (
        [json.loads(p.read_text(encoding="utf-8"))["usage"] for p in sorted(folder.glob("*.json"))]
        if folder.exists()
        else []
    )


def persist(root: Path, usage: dict, egress: dict) -> None:
    folder = root / ".mlca/requests"
    folder.mkdir(exist_ok=True)
    with FileLock(str(folder) + ".lock"):
        atomic_json(folder / f"{usage['request_id']}.json", {"usage": usage, "egress": egress})
        records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))]
        # The committed request envelopes are recoverable truth; ledgers are replaceable views.
        for category, filename in [("usage", "usage.jsonl"), ("egress", "egress.jsonl")]:
            temporary = root / ".mlca" / f".{filename}.tmp"
            temporary.write_text("".join(canonical(r[category]) + "\n" for r in records), encoding="utf-8")
            temporary.replace(root / ".mlca" / filename)


def summary(records: list[dict]) -> dict:
    groups = {}
    for axis in ["role", "event_id", "step_id", "principal"]:
        result = defaultdict(
            lambda: {
                "requests": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cached_tokens": 0,
                "known_cost_usd": 0.0,
                "unknown_cost_requests": 0,
                "latency_ms": 0.0,
            }
        )
        for r in records:
            group = result[str(r.get(axis))]
            group["requests"] += 1
            for key in ["input_tokens", "output_tokens", "cached_tokens", "latency_ms"]:
                group[key] += r.get(key, 0) or 0
            if r.get("cost_source") == "external":
                pass
            elif r.get("cost_usd") is None:
                group["unknown_cost_requests"] += 1
            else:
                group["known_cost_usd"] += r["cost_usd"]
        groups[axis] = dict(result)
    return {
        "requests": len(records),
        "model_requests": sum(r.get("role") != "mcp" for r in records),
        "external_tool_calls": sum(r.get("role") == "mcp" for r in records),
        "external_model_usage_unavailable": any(r.get("role") == "mcp" for r in records),
        "known_cost_usd": sum(r.get("cost_usd") or 0 for r in records),
        "unknown_cost_requests": sum(
            r.get("cost_usd") is None and r.get("cost_source") != "external" for r in records
        ),
        "groups": groups,
    }
