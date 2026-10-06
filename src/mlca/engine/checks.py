import importlib.util
import json
from pathlib import Path
from typing import Any

from mlca.log.schema import ProjectState
from mlca.paths import contained, sha256


def evaluate(
    spec: dict, state: ProjectState, root: Path, workflow: Any = None, event_id: Any = None
) -> tuple[bool, str]:
    kind = spec.get("type", "event_done" if "event_done" in spec else "")
    if kind == "event_done":
        name = spec.get("event_done", spec.get("event"))
        return state.event_statuses.get(name) == "done", f"Event {name} complete"
    if kind == "fact_present":
        fact = state.facts.get(spec["key"])
        passed = fact is not None
        if passed and "equals" in spec:
            passed = fact["value"] == spec["equals"]
        if passed and "predicate" in spec:
            predicate = spec["predicate"]
            value = fact["value"]
            passed = (
                value is not None
                if predicate == "not_null"
                else isinstance(value, (int, float)) and value > 0
                if predicate == "positive"
                else False
            )
        return passed, f"Fact {spec['key']} recorded"
    if kind == "output_exists":
        alternatives = spec.get("any_of", [{"action": spec.get("action"), "output": spec.get("output")}])
        for candidate in alternatives:
            for step in state.steps:
                if (
                    step["status"] != "completed"
                    or step["action_id"] != candidate["action"]
                    or (event_id is not None and step["event_id"] != event_id)
                    or step.get("generation", 0) != state.generations.get(step["event_id"], 0)
                ):
                    continue
                for output in step.get("outputs", []):
                    path = root / output["path"]
                    if (
                        output["name"] == candidate["output"]
                        and contained(path, root / ".mlca/steps")
                        and path.is_file()
                        and sha256(path) == output["sha256"]
                    ):
                        return True, "Output exists and hash matches"
        return False, "Required output missing or changed"
    if kind == "artefact_hash_recorded":
        paths = [spec["path"]] if "path" in spec else list(state.artefacts)
        return bool(paths) and all(
            p in state.artefacts and (root / p).is_file() and sha256(root / p) == state.artefacts[p]["sha256"]
            for p in paths
        ), "Artifact hashes"
    if kind == "metric_present":
        return any(
            m["name"] == spec["name"] and m["split"] == spec["split"]
            for s in state.steps
            if s["status"] == "completed"
            for m in s.get("metrics", [])
        ), "Metric recorded"
    if kind == "figure_count":
        return sum(len(s.get("figures", [])) for s in state.steps if s["status"] == "completed") >= spec[
            "min"
        ], "Figure count"
    if kind == "split_frozen":
        split = state.split
        passed = bool(split) and all(
            (root / split[k]["path"]).is_file() and sha256(root / split[k]["path"]) == split[k]["sha256"]
            for k in ["manifest", "train", "val", "vault"]
        )
        return passed, "Frozen split artifacts"
    if kind == "test_unlocked":
        return state.test_unlocked, "Test partition explicitly unlocked"
    if kind == "user_confirm":
        key = spec.get("subgoal_id", "")
        return f"{event_id}.{key}" in state.confirmations, "Explicit user confirmation"
    if kind == "fit_on_train_only":
        relevant = [
            s
            for s in state.steps
            if s["status"] == "completed"
            and s.get("event_id") in {"preprocess", "features", "model"}
            and s.get("generation", 0) == state.generations.get(s["event_id"], 0)
        ]
        if not relevant or not state.split:
            return False, "No completed fit evidence"
        for step in relevant:
            manifest = root / ".mlca/steps" / step["step_id"] / "manifest.json"
            data = json.loads(manifest.read_text())
            fits = data.get("fits", [])
            if not fits or any(
                f["partition"] != "train" or f["index_sha256"] != state.split["train_index_sha256"]
                for f in fits
            ):
                return False, "Fit missing or not aligned with frozen training indexes"
        return True, "Fit records match frozen training indexes (instrumentation limit applies)"
    if kind == "template_check":
        # Only trusted templates may load executable checks.
        if workflow is None:
            return False, "Workflow required"
        file = workflow.path / "checks.py"
        module_spec = importlib.util.spec_from_file_location("mlca_template_checks", file)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return getattr(module, spec["function"])(state.model_copy(deep=True), dict(state.artefacts))
    return False, f"Unknown check type: {kind}"


def run_all(state: Any, workflow: Any, root: Any, emit: Any) -> Any:
    event = workflow.events[state.current_event]
    results = []
    for subgoal in event.subgoals:
        spec = subgoal.check.model_dump()
        spec["subgoal_id"] = subgoal.id
        try:
            passed, detail = evaluate(spec, state, root, workflow, event.id)
        except (OSError, ValueError, KeyError) as exc:
            passed, detail = False, str(exc)
        results.append((subgoal, passed, detail))
    required = {s.id for s in event.subgoals} if event.done_when == "all_subgoals" else set(event.done_when)
    done = all(passed for subgoal, passed, _ in results if subgoal.id in required)
    for subgoal, passed, detail in results:
        emit(
            "SubgoalChecked",
            {
                "subgoal_id": subgoal.id,
                "check_type": subgoal.check.type,
                "passed": bool(passed),
                "detail": detail,
                "event_done": done,
            },
        )
    return done
