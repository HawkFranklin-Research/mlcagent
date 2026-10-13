"""Request envelopes are truth; summaries expose incomplete measurement explicitly."""

import csv
import json
from collections import defaultdict
from pathlib import Path

import yaml
from filelock import FileLock

from mlca.paths import atomic_json, canonical

TOKEN_FIELDS = ("input_tokens", "output_tokens", "reasoning_tokens", "cached_tokens", "cache_write_tokens")
SUM_FIELDS = (*TOKEN_FIELDS, "cost_usd", "upstream_cost_usd", "latency_ms")


def read(root: Path) -> list[dict]:
    folder = root / ".mlca/requests"
    return (
        [json.loads(p.read_text(encoding="utf-8"))["usage"] for p in sorted(folder.glob("*.json"))]
        if folder.exists()
        else []
    )


def _views(root: Path) -> None:
    folder = root / ".mlca/requests"
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(folder.glob("*.json"))]
    for category, filename in [("usage", "usage.jsonl"), ("egress", "egress.jsonl")]:
        temporary = root / ".mlca" / f".{filename}.tmp"
        temporary.write_text("".join(canonical(r[category]) + "\n" for r in records), encoding="utf-8")
        temporary.replace(root / ".mlca" / filename)


def persist(root: Path, usage: dict, egress: dict) -> None:
    folder = root / ".mlca/requests"
    folder.mkdir(exist_ok=True)
    with FileLock(str(folder) + ".lock"):
        atomic_json(folder / f"{usage['request_id']}.json", {"usage": usage, "egress": egress})
        _views(root)


def fill_missing(root: Path, request_id: str, values: dict) -> list[str]:
    """Merge only unavailable fields under the envelope lock; keep egress unchanged."""
    folder = root / ".mlca/requests"
    with FileLock(str(folder) + ".lock"):
        path = folder / f"{request_id}.json"
        if path.resolve().parent != folder.resolve():
            raise ValueError("Invalid request identifier")
        envelope = json.loads(path.read_text())
        record = envelope["usage"]
        changed = []
        for key, value in values.items():
            if value is not None and record.get(key) is None:
                record[key] = value
                changed.append(key)
        if "cost_usd" in changed:
            record["cost_source"] = "generation_endpoint"
        if changed:
            record.setdefault("backfill_fields", []).extend(changed)
            atomic_json(path, envelope)
            _views(root)
        return changed


def aggregate(records: list[dict]) -> dict:
    result = {"requests": len(records), "partial": False}
    for field in SUM_FIELDS:
        eligible = (
            [r for r in records if r.get("cost_source") != "external"]
            if field.endswith("cost_usd")
            else records
        )
        known = [r[field] for r in eligible if r.get(field) is not None]
        unknown = len(eligible) - len(known)
        result[field] = sum(known) if known or not eligible else None
        result[f"unknown_{field}_requests"] = unknown
        result["partial"] |= unknown > 0
    result["known_cost_usd"] = result["cost_usd"]
    result["unknown_cost_requests"] = result["unknown_cost_usd_requests"]
    return result


def summary(records: list[dict]) -> dict:
    groups = {}
    for axis in ["role", "event_id", "step_id", "principal", "model_reported", "provider_reported"]:
        buckets = defaultdict(list)
        for record in records:
            buckets[str(record.get(axis))].append(record)
        groups[axis] = {key: aggregate(values) for key, values in buckets.items()}
    # MCP tool envelopes do not represent model inference; imported client usage does.
    model_records = [r for r in records if r.get("role") != "mcp"]
    totals = aggregate(model_records)
    return {
        "requests": len(records),
        "model_requests": len(model_records),
        "external_tool_calls": len(records) - len(model_records),
        "external_model_usage_unavailable": any(r.get("role") == "mcp" for r in records),
        "known_cost_usd": totals["known_cost_usd"],
        "unknown_cost_requests": totals["unknown_cost_requests"],
        "totals": totals,
        "groups": groups,
    }


def measured_total(group: dict, field: str, source="exact") -> dict:
    """Keep evaluation's complete-total contract, also expose its known subtotal."""
    unknown = group[f"unknown_{field}_requests"]
    value = None if unknown else group[field]
    if not unknown:
        return {"value": value, "source": source if value is not None else "unavailable"}
    return {
        "value": value,
        "source": source if value is not None else "unavailable",
        "known_value": group[field],
        "unknown_requests": unknown,
        "partial": unknown > 0,
    }


def export_csv(root: Path, destination: Path) -> int:
    records = read(root)
    project = yaml.safe_load((root / ".mlca/project.yaml").read_text())
    fields = ["project_id", *sorted({k for r in records for k in r} - {"project_id"})]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = {
                k: canonical(v) if isinstance(v, (dict, list)) else v
                for k, v in record.items()
                if k != "project_id"
            }
            writer.writerow({"project_id": project["project_id"], **row})
    return len(records)
