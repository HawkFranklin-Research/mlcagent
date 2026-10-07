from pathlib import Path
from typing import Any

from mlca.paths import sha256


def build(root: Path, state: Any, requests: Any) -> Any:
    index = {r["request_id"]: r for r in requests}
    rows = []
    for step in state.steps:
        if step["status"] != "completed":
            continue
        calls = [
            index[s["worker_request_id"]]
            for s in step.get("scripts", [])
            if s.get("worker_request_id") in index
        ]
        calls.extend(r for r in requests if r.get("step_id") == step["step_id"] and r not in calls)
        chain = {
            "agent_file_access": "unknown (outside MLCA)",
            "step_id": step["step_id"],
            "event_id": step["event_id"],
            "action_id": step["action_id"],
            "params": step["params"],
            "scripts": step.get("scripts", []),
            "runs": step.get("runs", []),
            "inputs": step["inputs"],
            "model_requests": calls,
        }
        for output in step.get("outputs", []):
            file = root / output["path"]
            rows.append(
                {
                    "artifact": output,
                    "integrity_ok": file.is_file() and sha256(file) == output["sha256"],
                    **chain,
                }
            )
        for metric in step.get("metrics", []):
            rows.append(
                {"metric": metric, "source_manifest": f".mlca/steps/{step['step_id']}/manifest.json", **chain}
            )
    return rows
