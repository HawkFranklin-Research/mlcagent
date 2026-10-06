import re
import shutil
import time
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from ulid import ULID

from mlca.engine.split import freeze as freeze_split
from mlca.errors import BudgetError, IntegrityError, MlcaUserError
from mlca.paths import atomic_json, contained, directory_sha256, sha256
from mlca.project.env import python
from mlca.sandbox.level import detect
from mlca.sandbox.vault import exposed

from .artefacts import collect, freeze
from .process import execute
from .static_checks import check as static_check


def inputs_for(action: Any, state: Any, root: Any, params: Any = None) -> dict[str, Path]:
    params = params or {}
    paths = {}
    for item in action.inputs:
        ref = item["ref"]
        for key, value in params.items():
            ref = ref.replace("{" + key + "}", str(value))
        if ref == "registered_data" or ref in state.data:
            if state.split:
                raise MlcaUserError("Original registered data are not readable after split freezing")
            chosen = state.data if ref == "registered_data" else {ref: state.data[ref]}
            for name, data in chosen.items():
                path = Path(data["original_path"])
                if sha256(path) != data["sha256"]:
                    raise IntegrityError("Registered input hash changed")
                paths[name] = path
        elif ref in {"train", "val"}:
            if not state.split:
                raise MlcaUserError("Action requires a frozen split")
            entry = state.split[ref]
            path = root / entry["path"]
            if sha256(path) != entry["sha256"]:
                raise IntegrityError("Frozen partition changed")
            paths[ref] = path
        elif ref == "test":
            if not action.reads_test or not state.test_unlocked:
                raise MlcaUserError("Action cannot read the locked test partition")
            # Mounted only inside the exposure context, after the user unlock event.
        elif ref == "prior_outputs":
            for step in state.steps:
                if step["status"] != "completed" or step.get("generation", 0) != state.generations.get(
                    step["event_id"], 0
                ):
                    continue
                # Do not remount raw-derived EDA artifacts after freezing the split.
                if state.split and step["event_id"] in {"onboard", "data", "eda", "split"}:
                    continue
                if not action.reads_test and step["event_id"] in {"test", "interpret", "report"}:
                    continue
                for output in step.get("outputs", []):
                    path = root / output["path"]
                    if not contained(path, root / ".mlca/steps") or sha256(path) != output["sha256"]:
                        raise IntegrityError("Prior artifact changed")
                    paths[step["step_id"] + "/" + output["name"]] = path
                    if output["kind"] == "model" and step["event_id"] == "model":
                        paths["latest_model"] = path
        else:
            raise MlcaUserError(f"Unknown action input reference: {ref}")
    return paths


def _manifest(step: Any, output: Any, kind: Any) -> Any:
    atomic_json(
        step / "manifest.json",
        {"outputs": [{"name": output, "kind": kind}], "metrics": [], "facts": [], "fits": []},
    )


def run_step(session: Any, action: Any, params: Any) -> Any:
    started_at = time.monotonic()
    state = session.state
    environment_lock = session.root / ".mlca/requirements.lock"
    if not environment_lock.is_file() or sha256(environment_lock) != state.lock_sha256:
        raise IntegrityError(
            "Analysis environment lock differs from this branch; restore the recorded environment"
        )
    if directory_sha256(session.root / ".mlca/runtime/mlca_runtime") != state.runtime_sha256:
        raise IntegrityError("Frozen analysis runtime source changed")
    number = sum(r.type.value == "StepStarted" for r in session.store.read()) + 1
    step_id = f"{number:02d}_{action.event}_{action.id}_{str(ULID())[-8:]}"
    step = session.root / ".mlca/steps" / step_id
    step.mkdir(parents=True)
    (step / "outputs").mkdir()
    inputs = inputs_for(action, state, session.root, params)
    session.emit(
        "StepStarted",
        {
            "step_id": step_id,
            "action_id": action.id,
            "params": params,
            "inputs": {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()},
            "outputs": [o.model_dump() for o in action.outputs],
            "number": number,
            "generation": state.generations.get(action.event, 0),
            "environment_packages": state.environment_packages,
            "lock_sha256": state.lock_sha256,
            "runtime_sha256": state.runtime_sha256,
        },
        step_id=step_id,
    )
    atomic_json(step / "inputs.json", {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()})
    try:
        if action.builtin:
            result = _builtin(session, action, params, step_id, step, state)
        else:
            result = _worker(session, action, params, step_id, step, state, inputs)
        result["step_id"] = step_id
        result["wall_time_s"] = time.monotonic() - started_at
        atomic_json(step / "record.json", result)
        # Include runtime evidence in the indexed artifacts; metrics have a hashed manifest source.
        manifest = step / "manifest.json"
        result["outputs"].append(
            {
                "name": "manifest.json",
                "path": str(manifest.relative_to(session.root)),
                "sha256": sha256(manifest),
                "size": manifest.stat().st_size,
                "kind": "other",
                "caption": "",
            }
        )
        session.emit("StepCompleted", {k: v for k, v in result.items() if k != "facts"}, step_id=step_id)
        freeze(step)
        return result
    except Exception as exc:
        session.emit(
            "StepFailed",
            {
                "step_id": step_id,
                "attempts": len(list((step / "attempts").glob("*"))),
                "last_error": session.redact(str(exc))[:2000],
            },
            step_id=step_id,
        )
        raise


def _builtin(session: Any, action: Any, params: Any, step_id: Any, step: Any, state: Any) -> Any:
    started_at = time.monotonic()
    # Engine actions are reproducible operations with parameters, not LLM-written privileged code.
    script = """# Engine-managed action. Reproduce through mlca replay --verify.\n"""
    (step / "script.py").write_text(script)
    session.emit(
        "ScriptWritten",
        {
            "attempt": 1,
            "sha256": sha256(step / "script.py"),
            "path": str((step / "script.py").relative_to(session.root)),
            "builtin": action.builtin,
        },
        step_id=step_id,
    )
    output = action.outputs[0]
    if action.builtin == "split":
        value = freeze_split(session.root, state, params, step_id, session.emit)
    elif action.builtin == "inventory":
        value = {"brief": state.brief, "inventory": state.inventory}
    else:
        from mlca.report import generate

        value = generate(session.root, state, session.workflow, session.branches.records(), "all")
    atomic_json(step / "outputs" / output.name, value)
    _manifest(step, output.name, output.kind)
    session.emit(
        "RunFinished",
        {
            "attempt": 1,
            "exit_status": 0,
            "duration": time.monotonic() - started_at,
            "sandbox_level": "engine",
            "builtin": action.builtin,
        },
        step_id=step_id,
    )
    return collect(session.root, step, action, session.state)


def _worker(session: Any, action: Any, params: Any, step_id: Any, step: Any, state: Any, inputs: Any) -> Any:
    from mlca.roles.worker import Worker

    worker = Worker(session)
    level = detect(session.config.sandbox.allow_level_b)
    source, error, request_id = "", None, None
    max_attempts = session.config.budgets.worker_max_attempts
    context = exposed(session.root, state, step_id, session.emit) if action.reads_test else nullcontext(None)
    with context as test_path:
        if test_path:
            inputs["test"] = test_path
            atomic_json(
                step / "inputs.json", {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()}
            )
        for attempt in range(1, max_attempts + 1):
            directory = step / "attempts" / str(attempt)
            directory.mkdir(parents=True)
            (directory / "outputs").mkdir()
            (directory / "scratch").mkdir()
            atomic_json(
                directory / "inputs.json",
                {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()},
            )
            try:
                if error is None:
                    source, request_id = worker.write_script(action, params, inputs, state, step_id)
                else:
                    source, request_id = worker.repair_script(action, source, error, step_id)
            except BudgetError:
                raise
            except MlcaUserError as exc:
                error = str(exc)
                if attempt == max_attempts:
                    raise
                continue
            script = directory / "script.py"
            script.write_text(source)
            script_hash = sha256(script)
            session.emit(
                "ScriptWritten",
                {
                    "attempt": attempt,
                    "sha256": script_hash,
                    "path": str(script.relative_to(session.root)),
                    "worker_request_id": request_id,
                },
                step_id=step_id,
            )
            violations = static_check(
                source, action.allow_network, require_fit=action.event in {"preprocess", "features", "model"}
            )
            if action.event not in {"preprocess", "features", "model"}:
                import ast

                tree = ast.parse(source) if not violations else None
                if tree and any(
                    isinstance(n, ast.Call)
                    and (
                        getattr(n.func, "attr", None) in {"fit", "fit_transform", "fit_record", "partial_fit"}
                        or getattr(n.func, "id", None) == "fit_record"
                    )
                    for n in ast.walk(tree)
                ):
                    violations.append("Fitting is not allowed in this workflow event")
            if violations:
                session.emit(
                    "StaticCheckFailed", {"attempt": attempt, "violations": violations}, step_id=step_id
                )
                error = "\n".join(violations)
                continue
            execution = execute(
                python(session.root / ".mlca/env"),
                directory,
                list(inputs.values()),
                session.root / ".mlca/env",
                session.root / ".mlca/runtime",
                session.root / ".mlca/style.mplstyle",
                level,
                action.timeout_s,
                state.split["train_index_sha256"] if state.split else "",
                action.allow_network,
                callback=session.output_callback,
            )
            execution = {k: session.redact(v) if isinstance(v, str) else v for k, v in execution.items()}
            session.emit("RunFinished", {"attempt": attempt, **execution}, step_id=step_id)
            if execution["exit_status"] != 0 or sha256(script) != script_hash:
                if session.config.privacy.allow_sample_rows:
                    error = execution["stderr"][-4000:] or "Execution failed or script was modified"
                else:
                    diagnostics = execution["stderr"]
                    types = re.findall(
                        r"^([A-Za-z][A-Za-z0-9_]*(?:Error|Exception))(?::|$)", diagnostics, re.MULTILINE
                    )
                    locations = re.findall(r'File "[^"\n]*script.py", line (\d+)', diagnostics)
                    error = "Execution failed: " + (types[-1] if types else "runtime failure")
                    if locations:
                        error += "; script line " + locations[-1]
                    error += ". Detailed diagnostics remain local because sample-row egress is disabled."
                continue
            try:
                collect(session.root, directory, action, state)
            except MlcaUserError as exc:
                error = str(exc)
                continue
            shutil.copyfile(script, step / "script.py")
            shutil.copytree(directory / "outputs", step / "outputs", dirs_exist_ok=True)
            manifest = directory / "manifest.json"
            if not manifest.exists():
                atomic_json(manifest, {"outputs": [], "metrics": [], "fits": [], "facts": []})
            shutil.copyfile(manifest, step / "manifest.json")
            return collect(session.root, step, action, state)
    raise MlcaUserError("Worker exhausted its attempt budget: " + (error or "No valid script"))
