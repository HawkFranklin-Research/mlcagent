"""Compact evidence views. Data-derived text never supplies the result summary."""

from mlca.config import redact_value


def work_order(order):
    result = dict(order)
    # Prompt is supplied for parity with Worker; its interpolated content is untrusted data.
    if "worker_prompt" in result:
        result["worker_prompt_data"] = result.pop("worker_prompt")
    result["brief_data"] = result.pop("brief", {})
    result["inputs_data"] = result.pop("inputs", {})
    return result


def step(saved):
    result = {k: saved[k] for k in ("step_id", "status", "phase", "attempt", "poll_after_s") if k in saved}
    result.setdefault("phase", saved.get("status", "starting"))
    if saved.get("work_order") and saved["status"] == "awaiting_script":
        result["work_order"] = work_order(saved["work_order"])
        result["attempts_left"] = max(0, saved["work_order"]["max_attempts"] - saved["attempt"] + 1)
    if saved.get("scripts"):
        result["attempt"] = len(saved["scripts"])
    if saved.get("runs"):
        result["elapsed_s"] = sum(r.get("duration", 0) for r in saved["runs"])
        result["last_run"] = {
            k: saved["runs"][-1].get(k) for k in ("exit_status", "duration", "sandbox_level")
        }
    if saved.get("last_error"):
        result["diagnostics_data"] = saved["last_error"]
    if saved.get("error"):
        result["diagnostics_data"] = saved["error"]
    if saved["status"] == "completed":
        result["outputs_data"] = saved.get("outputs", [])
        result["metrics_data"] = saved.get("metrics", [])
    return result


def result(value, config, summary="MLCA request completed."):
    return redact_value({"summary": summary, "data": value}, config)
