from collections import Counter
from typing import Any

from mlca.llm.usage import summary


def build(state: Any, requests: Any, records: Any) -> Any:
    decisions = {
        "OptionChosen",
        "CustomInstructionSubmitted",
        "UserConfirmed",
        "PackageApproved",
        "ScriptEditedByUser",
        "TestUnlocked",
        "BranchCreated",
        "BranchCheckedOut",
        "ApprovalResolved",
    }
    principals = Counter(r.actor for r in records if r.type.value in decisions)
    script_sources = Counter(
        script.get("source", "worker")
        for step in state.steps
        for script in step.get("scripts", [])
        if not script.get("builtin")
    )
    return {
        "model_changes": [
            {"record_id": r.id, "actor": r.actor, **r.payload}
            for r in records
            if r.type.value == "ModelChanged"
        ],
        "model_answers": [
            {k: r.get(k) for k in ("request_id", "step_id", "role", "model", "model_reported")}
            for r in requests
            if r.get("role") not in {"mcp", "external_agent"}
        ],
        "agent_file_access": "unknown (outside MLCA)",
        "decisions_by_principal": dict(principals),
        "script_attempts_by_source": dict(script_sources),
        **summary(requests),
        "steps_completed": sum(s["status"] == "completed" for s in state.steps),
        "steps_failed": sum(s["status"] == "failed" for s in state.steps),
        "worker_attempts": sum(len(s.get("scripts", [])) for s in state.steps),
        "repairs": sum(max(0, len(s.get("scripts", [])) - 1) for s in state.steps),
        "wall_time_s": sum(s.get("wall_time_s", 0) for s in state.steps),
        "compute_time_s": sum(r.get("duration", 0) for s in state.steps for r in s.get("runs", [])),
        "llm_latency_s": sum(r.get("latency_ms", 0) for r in requests if r.get("role") != "mcp") / 1000,
        "mcp_tool_time_s": sum(r.get("duration_s", 0) for r in requests if r.get("role") == "mcp"),
        "human_interventions": {
            k: sum(r.type.value == k and r.actor == "user" for r in records)
            for k in [
                "OptionChosen",
                "CustomInstructionSubmitted",
                "UserConfirmed",
                "PackageApproved",
                "ScriptEditedByUser",
                "TestUnlocked",
            ]
        },
        "scope_rejections": sum(
            r.type.value == "ScopeDecision" and r.payload["decision"] == "reject" for r in records
        ),
    }
