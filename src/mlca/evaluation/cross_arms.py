"""One sourced row per arm/client/model/task; unavailable fields stay null."""

import csv
import json
from collections import defaultdict

from mlca.paths import atomic_json


def summarize(root):
    groups = defaultdict(list)
    for path in sorted(root.rglob("bench_summary.json")):
        s = json.loads(path.read_text())
        key = (
            s.get("measurement_arm"),
            s.get("mode", "driver"),
            s.get("client"),
            s.get("model"),
            s.get("task"),
        )
        groups[key].append((path, s))
    rows = []
    for key, values in groups.items():
        n = sum(s["run_count"]["value"] for _, s in values)
        completed = sum(s["completed"]["value"] for _, s in values)
        row = dict(zip(("arm", "mode", "client", "model", "task"), key))
        row.update(
            runs=n,
            completed=completed,
            completion_rate=completed / n if n else None,
            navigator_fallbacks=None
            if key[1] == "brain"
            else sum(s["navigator_fallbacks"]["value"] or 0 for _, s in values),
            sources=[str(p.relative_to(root)) for p, _ in values],
        )
        for section in ("time", "tokens", "interventions"):
            keys = {field for _, s in values for field in s.get(section, {})}
            for field in sorted(keys):
                stats = [s.get(section, {}).get(field) for _, s in values]
                available = [v for v in stats if v and v.get("mean", {}).get("value") is not None]
                count = sum(v["n"]["value"] for v in available)
                row[section + "." + field + ".mean"] = (
                    sum(v["mean"]["value"] * v["n"]["value"] for v in available) / count if count else None
                )
                row[section + "." + field + ".unavailable"] = sum(
                    v["unavailable"]["value"] for v in stats if v
                )
        row["failures"] = {
            category: sum(s.get("failures", {}).get(category, {}).get("value", 0) for _, s in values)
            for category in {c for _, s in values for c in s.get("failures", {})}
        }
        rows.append(row)
    atomic_json(
        root / "cross_arm_summary.json",
        {
            "groups": rows,
            "numeric_source": "derived; client tokens retain client-reported provenance in source summaries",
        },
    )
    with (root / "cross_arm_summary.csv").open("w", newline="") as f:
        fields = [
            "arm",
            "mode",
            "client",
            "model",
            "task",
            "runs",
            "completed",
            "completion_rate",
            "navigator_fallbacks",
        ]
        fields += sorted({k for row in rows for k in row if k not in {*fields, "sources", "failures"}})
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerows({k: "n/a" if row.get(k) is None else row[k] for k in fields} for row in rows)
    return {"groups": rows}
