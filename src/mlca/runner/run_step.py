import re
import shutil
import time
from contextlib import ExitStack, nullcontext
from pathlib import Path
from typing import Any

from ulid import ULID

from mlca.engine.split import freeze as freeze_split
from mlca.errors import BudgetError, IntegrityError, MlcaUserError
from mlca.paths import atomic_json, canonical, contained, directory_sha256, sha256
from mlca.project.env import python
from mlca.sandbox.level import detect
from mlca.sandbox.vault import exposed

from .artefacts import collect, freeze
from .process import execute
from .static_checks import check as static_check

INTERPRET_ROWS = 10000


def inputs_for(action: Any, state: Any, root: Any, params: Any = None) -> dict[str, Path]:
    params = params or {}
    paths = {}
    for item in action.inputs:
        ref = item["ref"]
        for key, value in params.items():
            ref = ref.replace("{" + key + "}", str(value))
        if ref == "registered_data" or (ref in state.data and ref != "external"):
            if state.split:
                raise MlcaUserError("Original registered data are not readable after split freezing")
            if ref in state.data and state.data[ref].get("role") == "external":
                raise MlcaUserError(
                    "External cohorts are sealed; use the external input after test unlock",
                    category="test_lock",
                )
            chosen = (
                {n: d for n, d in state.data.items() if d.get("role") != "external"}
                if ref == "registered_data"
                else {ref: state.data[ref]}
            )
            if ref == "registered_data" and state.primary_data in chosen:
                chosen = {state.primary_data: chosen[state.primary_data], **chosen}
            for name, data in chosen.items():
                path = Path(data["original_path"])
                if sha256(path) != data["sha256"]:
                    raise IntegrityError("Registered input hash changed")
                if name == state.primary_data and state.prepared_data:
                    path = root / state.prepared_data["path"]
                    if sha256(path) != state.prepared_data["sha256"]:
                        raise IntegrityError("Prepared input changed")
                paths[name] = path
        elif ref in {"train", "val"}:
            if not state.split:
                raise MlcaUserError("Action requires a frozen split")
            entry = state.split[ref]
            path = root / entry["path"]
            if sha256(path) != entry["sha256"]:
                raise IntegrityError("Frozen partition changed")
            paths[ref] = (
                interpretation_sample(root, ref, path, entry["sha256"])
                if action.event == "interpret"
                else path
            )
        elif ref == "external":
            if not state.test_unlocked or action.event not in {"test", "interpret"}:
                raise MlcaUserError("External cohort is locked", category="test_lock")
        elif ref == "test":
            if not action.reads_test or not state.test_unlocked:
                raise MlcaUserError("Action cannot read the locked test partition", category="test_lock")
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
    from types import SimpleNamespace

    from mlca.engine.data_review import protocol_input

    paths["_protocol"] = protocol_input(SimpleNamespace(root=root, state=state))
    return paths


def interpretation_sample(root: Any, ref: str, path: Path, digest: str) -> Path:
    """Interpretation reads at most INTERPRET_ROWS rows per partition: a fixed-seed sample of a larger
    partition, kept in its original order. Diagnostics fit nothing, so a sample bounds their cost."""
    import numpy as np
    import pandas as pd
    import pyarrow.parquet as pq

    rows = pq.ParquetFile(path).metadata.num_rows
    if rows <= INTERPRET_ROWS:
        return path
    sample = root / ".mlca/samples" / f"{ref}-{digest[:16]}.parquet"
    if not sample.is_file():
        sample.parent.mkdir(parents=True, exist_ok=True)
        chosen = np.sort(np.random.default_rng(0).choice(rows, INTERPRET_ROWS, replace=False))
        temporary = sample.with_suffix(".tmp")
        pd.read_parquet(path).iloc[chosen].to_parquet(temporary, index=True)
        temporary.replace(sample)
    return sample


def source_columns(state: Any, root: Any) -> list[str] | None:
    """Columns of the frozen training partition, without the stored row index."""
    if not state.split:
        return None
    import pyarrow.parquet as pq

    schema = pq.read_schema(root / state.split["train"]["path"])
    index = {i for i in (schema.pandas_metadata or {}).get("index_columns", []) if isinstance(i, str)}
    return [name for name in schema.names if name not in index]


def protected_columns(state: Any) -> list[str]:
    """Columns fit_record refuses as inputs: outcomes, exclusions and the group key.
    Survival fits keep their duration and event columns, which Cox models read from X."""
    names = set(state.excluded_columns or []) | set(state.task.get("targets") or [])
    if state.group_column:
        names.add(state.group_column)
    for value in (state.columns or {}).values():
        names.update([value] if isinstance(value, str) else value or [])
    if state.template_id == "survival":
        names -= {state.columns.get("duration"), state.columns.get("event_column")}
        names -= set(state.task.get("targets") or [])
    names.discard("")
    return sorted(n for n in names if isinstance(n, str))


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
    inputs = inputs_for(action, state, session.root, params)
    step.mkdir(parents=True)
    (step / "outputs").mkdir()
    session.emit(
        "StepStarted",
        {
            "step_id": step_id,
            "mode": session.mode,
            "measurement_arm": session.measurement_arm,
            "action_id": action.id,
            "params": params,
            "inputs": {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()},
            "outputs": [o.model_dump() for o in action.outputs],
            "number": number,
            "generation": state.generations.get(action.event, 0),
            "environment_packages": state.environment_packages,
            "lock_sha256": state.lock_sha256,
            "runtime_sha256": state.runtime_sha256,
            "action_spec": action.model_dump(mode="json"),
            "turn_id": session.turn_id,
        },
        step_id=step_id,
    )
    atomic_json(step / "inputs.json", {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()})
    try:
        if action.builtin:
            result = _builtin(session, action, params, step_id, step, state)
        else:
            result = _worker(session, action, params, step_id, step, state, inputs)
        if result.get("status") == "awaiting_script":
            return result
        return complete_step(session, action, step_id, result, started_at)
    except Exception as exc:
        session.emit(
            "StepFailed",
            {
                "step_id": step_id,
                "attempts": len(list((step / "attempts").glob("*"))),
                "last_error": session.redact(str(exc))[:2000],
                "category": getattr(exc, "category", "runtime_error:" + type(exc).__name__),
            },
            step_id=step_id,
        )
        freeze(step)
        raise


def complete_step(session, action, step_id, result, started_at=None):
    step = session.root / ".mlca/steps" / step_id
    result["step_id"] = step_id
    result["wall_time_s"] = (
        time.monotonic() - started_at
        if started_at is not None
        else sum(r.get("duration", 0) for r in session.step_status(step_id).get("runs", []))
    )
    atomic_json(step / "record.json", result)
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


def _builtin(session: Any, action: Any, params: Any, step_id: Any, step: Any, state: Any) -> Any:
    started_at = time.monotonic()
    # Engine actions are reproducible operations with parameters, not LLM-written privileged code.
    script = """# Engine-managed action. Reproduce through mlca replay --verify.\n"""
    (step / "script.py").write_text(script, encoding="utf-8")
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
        value = {"brief": state.brief, "inventory": state.inventory, "columns": state.columns}
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


def work_order(session, action, params, step_id, inputs, attempt, error=None):
    from mlca.roles.worker import render_order

    order = render_order(session, action, params, inputs, session.state)
    order.update(step_id=step_id, attempt=attempt, max_attempts=session.config.budgets.worker_max_attempts)
    if error:
        order["previous_diagnostics"] = error
    from mlca.config import redact_value

    order = redact_value(order, session.config)
    if session.mode == "brain":
        session.progress(
            "awaiting_script", attempt=attempt, max_attempts=session.config.budgets.worker_max_attempts
        )
    session.emit(
        "ScriptRequested",
        {
            "attempt": attempt,
            "work_order": order,
            "sha256": __import__("hashlib").sha256(canonical(order).encode()).hexdigest(),
        },
        step_id=step_id,
    )
    return order


def diagnostics(execution, allow_samples):
    if allow_samples:
        return execution["stderr"][-4000:] or "Execution failed or script was modified"
    text = execution["stderr"]
    types = re.findall(
        r"^(?:[A-Za-z_]\w*\.)*([A-Za-z][A-Za-z0-9_]*(?:Error|Exception))(?::|$)", text, re.MULTILINE
    )
    lines = re.findall(r'File "[^"\n]*script.py", line (\d+)', text)
    # MLCA's own runtime messages are written without data values, so they may leave the machine.
    helpers = re.findall(r'File "[^"\n]*mlca_runtime[/\\]__init__\.py", line \d+, in (\w+)', text)
    own = re.findall(
        r"^(?:[A-Za-z_]\w*\.)*[A-Za-z]\w*(?:Error|Exception): (MLCA: [^\n]{1,300})$", text, re.MULTILINE
    )
    hints = []
    # Fixed library-contract hints carry no captured values, columns or traceback text.
    if "Specifying the columns using strings is only supported for dataframes" in text:
        hints.append(
            "A string-column pipeline needs the original pandas feature DataFrame, not an array or already-transformed matrix."
        )
    if "ValueError: columns are missing:" in text:
        hints.append(
            "A complete saved pipeline expects original raw feature columns; do not preprocess or select a second time before prediction."
        )
    if "Some column names are not columns of the dataframe" in text:
        hints.append(
            "A named-column transformer received renamed or already-transformed features; "
            "inspect feature_names_in_ and the saved pipeline steps, and avoid applying preprocessing twice."
        )
    if "Unable to configure output for" in text and "set_output" in text:
        hints.append(
            "A custom transformer does not implement sklearn's set_output interface; "
            "prefer importable built-in transformers with get_feature_names_out support."
        )
    if "AttributeError: Can't get attribute" in text and "__main__" in text:
        hints.append(
            "A saved object references a function or class local to an earlier script. "
            "Use importable built-in estimators; joblib does not fix missing definitions. "
            "Never invent a dummy class to make an incompatible artifact load."
        )
    if re.search(r"TypeError: '(?:dict|_Inputs)' object is not callable", text):
        hints.append(
            "inputs() returns a dictionary of Paths; call the helper once, then index the returned dictionary."
        )
    if "unexpected keyword argument 'pos_label'" in text and "roc_auc_score" in text:
        hints.append(
            "roc_auc_score has no pos_label argument. For binary AUC, explicitly binarize "
            "the target against the declared positive label and align the probability column "
            "with estimator.classes_; for multiclass AUC align all probability columns."
        )
    if "multiclass-multioutput is not supported" in text or (
        "Classification metrics can't handle a mix of" in text
    ):
        hints.append(
            "Score categorical outputs separately in declared target order, with matching "
            "true/predicted label types. Reuse training-fitted target encoders unchanged; "
            "never fit an encoder during validation or test."
        )
    if "Pipeline" in text and (
        "has no attribute 'predict'" in text or "has no attribute 'inverse_transform'" in text
    ):
        hints.append(
            "Inspect each Pipeline's final estimator separately: PCA reconstructs with its final inverse_transform after transform, while MLPRegressor reconstructs with predict. Compare both in the same fitted frontend space, without preprocessing twice."
        )
    if "MLCA: row outputs require row_id and partition" in text:
        hints.append(
            "Do not create undeclared row artifacts. If a per-row output is required, row_id and partition must be explicit columns, not merely an index; otherwise save only the declared summary outputs."
        )
    if "'NoneType' object has no attribute 'shape'" in text:
        hints.append(
            "An expected array is None. Check missing returns and in-place routines: sklearn's private ACTIVATIONS mutate their array and return None. Use public numeric activation results and explicitly return the finite two-dimensional embedding matrix."
        )
    return (
        "Execution failed: "
        + (types[-1] if types else "runtime failure")
        + ("; script line " + lines[-1] if lines else "")
        + ("; inside mlca_runtime." + helpers[-1] if helpers else "")
        + (". " + own[-1] if own else "")
        + (". " + " ".join(hints) if hints else "")
        + ". Detailed diagnostics remain local because sample-row egress is disabled."
    )


def run_attempt(session, action, params, step_id, attempt, source, request_id=None):
    # Both script sources use this exact execution and collection path.
    state = session.state
    if (
        sha256(session.root / ".mlca/requirements.lock") != state.lock_sha256
        or directory_sha256(session.root / ".mlca/runtime/mlca_runtime") != state.runtime_sha256
    ):
        raise IntegrityError("Step environment or frozen runtime changed")
    step = session.root / ".mlca/steps" / step_id
    inputs = inputs_for(action, state, session.root, params)
    level = detect(session.config.sandbox.allow_level_b)
    directory = step / "attempts" / str(attempt)
    directory.mkdir(parents=True)
    (directory / "outputs").mkdir()
    (directory / "scratch").mkdir()
    script = directory / "script.py"
    source = session.redact(source)
    script.write_text(source, encoding="utf-8")
    script_hash = sha256(script)
    session.emit(
        "ScriptWritten",
        {
            "attempt": attempt,
            "sha256": script_hash,
            "path": str(script.relative_to(session.root)),
            "worker_request_id": request_id,
            "source": session.principal if session.mode == "brain" else session.measurement_arm,
        },
        step_id=step_id,
        actor=session.principal if session.mode == "brain" else "worker",
    )
    session.progress(
        "Checking the script", attempt=attempt, max_attempts=session.config.budgets.worker_max_attempts
    )
    violations = static_check(
        source, action.allow_network, require_fit=action.event in {"preprocess", "features", "model"}
    )
    if action.event not in {"preprocess", "features", "model"} and not violations:
        import ast

        if any(
            isinstance(n, ast.Call)
            and (
                getattr(n.func, "attr", None) in {"fit", "fit_transform", "fit_record", "partial_fit"}
                or getattr(n.func, "id", None) == "fit_record"
            )
            for n in ast.walk(ast.parse(source))
        ):
            violations.append("Fitting is not allowed in this workflow event")
    if violations:
        session.emit(
            "StaticCheckFailed",
            {
                "attempt": attempt,
                "violations": violations,
                "category": "fit_rule" if any("fit" in v.lower() for v in violations) else "static_check",
            },
            step_id=step_id,
        )
        return None, "\n".join(violations)
    # Exposure lasts for execution only, never while a provider or external agent is thinking.
    context = exposed(session.root, state, step_id, session.emit) if action.reads_test else nullcontext(None)
    with ExitStack() as stack:
        test_path = stack.enter_context(context)
        if (
            state.external
            and action.event in {"test", "interpret"}
            and (action.reads_test or any(i["ref"] == "external" for i in action.inputs))
        ):
            from mlca.sandbox.vault import exposed_external

            inputs.update(stack.enter_context(exposed_external(session, step_id)))
        if test_path:
            inputs["test"] = test_path
        mapping = {k: {"path": str(v), "sha256": sha256(v)} for k, v in inputs.items()}
        atomic_json(step / "inputs.json", mapping)
        atomic_json(directory / "inputs.json", mapping)
        session.progress(
            "Running in the sandbox", attempt=attempt, max_attempts=session.config.budgets.worker_max_attempts
        )
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
            expected_train_rows=state.split["counts"]["train"] if state.split else 0,
            protected_columns=protected_columns(state),
            event=action.event,
            source_columns=source_columns(state, session.root),
        )
    execution = {k: session.redact(v) if isinstance(v, str) else v for k, v in execution.items()}
    session.emit("RunFinished", {"attempt": attempt, **execution}, step_id=step_id)
    if execution["exit_status"] != 0 or sha256(script) != script_hash:
        return None, diagnostics(execution, session.config.privacy.allow_sample_rows)
    session.progress(
        "Collecting outputs", attempt=attempt, max_attempts=session.config.budgets.worker_max_attempts
    )
    try:
        collect(session.root, directory, action, state)
    except MlcaUserError as exc:
        session.emit("AttemptFailed", {"attempt": attempt, "category": exc.category}, step_id=step_id)
        return None, str(exc)
    shutil.copyfile(script, step / "script.py")
    shutil.copytree(directory / "outputs", step / "outputs", dirs_exist_ok=True)
    manifest = directory / "manifest.json"
    if not manifest.exists():
        atomic_json(manifest, {"outputs": [], "metrics": [], "fits": [], "facts": []})
    shutil.copyfile(manifest, step / "manifest.json")
    return collect(session.root, step, action, state), None


def _worker(session, action, params, step_id, step, state, inputs):
    from .sources import ExternalSource, WorkerSource

    if session.measurement_arm == "reference":
        from .reference import ReferenceSource

        source = ReferenceSource()
    else:
        source = ExternalSource() if session.mode == "brain" else WorkerSource(session)
    previous, error = "", None
    attempts = 1 if session.measurement_arm == "reference" else session.config.budgets.worker_max_attempts
    for attempt in range(1, attempts + 1):
        if session.mode != "brain":
            session.progress(
                "Writing the script" if not error else "Repairing the script",
                attempt=attempt,
                max_attempts=session.config.budgets.worker_max_attempts,
                reason=error or "",
            )
        order = work_order(session, action, params, step_id, inputs, attempt, error)
        if isinstance(source, ExternalSource):
            return {"step_id": step_id, "status": "awaiting_script", "work_order": order}
        try:
            previous, request_id = source.script(action, params, inputs, state, step_id, previous, error)
        except BudgetError:
            raise
        except MlcaUserError as exc:
            if exc.category == "provider_error":
                # The model never answered (rate limit, outage): not a code attempt, never a "repair".
                raise
            error = str(exc)
            continue
        observation, error = run_attempt(session, action, params, step_id, attempt, previous, request_id)
        if observation is not None:
            return observation
    failures = [r for r in session.store.read() if r.step_id == step_id and r.payload.get("category")]
    category = failures[-1].payload["category"] if failures else "provider_error"
    raise MlcaUserError(
        (
            "Reference step failed: "
            if session.measurement_arm == "reference"
            else "Worker exhausted its attempt budget: "
        )
        + (error or "No valid script"),
        category=category,
    )


def submit(session, step_id, code):
    from mlca.templates.model import ActionSpec

    saved = next((s for s in session.state.steps if s["step_id"] == step_id), None)
    if saved is None or saved["status"] != "awaiting_script":
        raise MlcaUserError("Step is not awaiting a script")
    if saved["event_id"] != session.state.current_event:
        raise MlcaUserError("Step belongs to another event")
    action = ActionSpec.model_validate(saved["action_spec"])
    attempt = saved["attempt"]
    observation, error = run_attempt(session, action, saved["params"], step_id, attempt, code)
    if observation is not None:
        observation = complete_step(session, action, step_id, observation)
        from mlca.engine.turn import finish

        return finish(session, action, observation)
    if attempt >= session.config.budgets.worker_max_attempts:
        session.emit(
            "StepFailed",
            {
                "step_id": step_id,
                "attempts": attempt,
                "last_error": error,
                "category": next(
                    (
                        r.payload["category"]
                        for r in reversed(session.store.read())
                        if r.step_id == step_id and r.payload.get("category")
                    ),
                    "runtime_error:ProcessError",
                ),
            },
            step_id=step_id,
        )
        freeze(session.root / ".mlca/steps" / step_id)
        return {"step_id": step_id, "status": "failed", "diagnostics": error}
    order = work_order(
        session,
        action,
        saved["params"],
        step_id,
        inputs_for(action, session.state, session.root, saved["params"]),
        attempt + 1,
        error,
    )
    return {"step_id": step_id, "status": "awaiting_script", "work_order": order}
