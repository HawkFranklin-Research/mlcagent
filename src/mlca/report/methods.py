from typing import Any


def build(state: Any, workflow: Any) -> Any:
    lines = [
        "# Methods draft",
        "",
        "Draft generated from the event log. Author review is required.",
        "Agent file access: unknown (outside MLCA).",
        "",
        f"Workflow: {workflow.spec.id} {workflow.spec.version}",
        f"Measurement arm: {state.measurement_arm}",
        f"Task: {state.task or 'legacy template defaults'}",
        f"Resolved columns: {state.columns}",
        f"Environment lock: {state.lock_sha256}",
        "",
    ]
    if state.measurement_arm == "reference":
        lines.extend(
            [
                "No-AI reference comparison: frozen engine-owned scripts; no model inference.",
                "Cox encoding omits the first category level; constant design columns are removed before fitting."
                if state.template_id == "survival"
                else "Classification families and validation selection are prespecified.",
                "",
            ]
        )
    lines.extend(["Recorded packages:", *state.environment_packages, ""])
    if state.split:
        lines.extend(
            [
                "Frozen split parameters:",
                str(state.split["parameters"]),
                f"Split manifest SHA256: {state.split['sha256']}",
                "",
            ]
        )
    if state.data_decisions:
        lines.extend(["## Pre-split data decisions", ""])
        for decision in state.data_decisions:
            lines.append(
                f"- {decision['rule']}: {decision['effect']} (actor: {decision.get('actor', 'unavailable')})"
            )
        lines.append("")
    for step in state.steps:
        if step["status"] != "completed":
            continue
        action = workflow.actions.get(step["action_id"])
        text = action.methods_text if action else "Scoped custom action."
        lines.extend([f"## {step['step_id']}", text or action.title, f"Parameters: {step['params']}", ""])
    return "\n".join(lines) + "\n"
