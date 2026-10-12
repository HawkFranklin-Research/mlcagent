import json
import shutil
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Any

from mlca.engine.split import partitions
from mlca.errors import IntegrityError
from mlca.paths import atomic_json, directory_sha256, sha256
from mlca.project.env import create, python
from mlca.project.init import column_for, primary_for
from mlca.project.inventory import read_table
from mlca.sandbox.level import detect
from mlca.sandbox.vault import exposed

from .process import execute


def verify(session: Any) -> Any:
    """Explicitly requested script reproduction, never invoked at session open."""
    records = session.branches.records(session.branch_name)
    state = session.state
    lock = session.root / ".mlca/requirements.lock"
    if not lock.is_file() or sha256(lock) != state.lock_sha256:
        raise IntegrityError("Environment lock no longer matches the log")
    results = []
    mapping = {}
    with tempfile.TemporaryDirectory(prefix="mlca-replay-") as temporary:
        root = Path(temporary)
        (root / ".mlca").mkdir()
        runtime_source = session.root / ".mlca/runtime/mlca_runtime"
        if directory_sha256(runtime_source) != state.runtime_sha256:
            raise IntegrityError("Frozen runtime source changed")
        environments = {}
        level = detect(session.config.sandbox.allow_level_b)
        for step in state.steps:
            if step["status"] != "completed":
                continue
            historical = session.root / ".mlca/steps" / step["step_id"]
            script = historical / "script.py"
            if sha256(script) != step["scripts"][-1]["sha256"]:
                raise IntegrityError("Historical script changed")
            builtin = step["scripts"][-1].get("builtin")
            if builtin:
                # Built-in operations are reproduced by engine code, not privileged generated scripts.
                if builtin == "split":
                    split = next(
                        r.payload
                        for r in records
                        if r.type.value == "SplitFrozen" and r.payload["split_id"] == step["step_id"]
                    )
                    data = state.data[split.get("primary_data") or primary_for(state)]
                    source = Path(data["original_path"])
                    if sha256(source) != data["sha256"]:
                        raise IntegrityError("Original input changed")
                    frame = read_table(source).reset_index(drop=True)
                    assigned = partitions(frame, split["parameters"], column_for(state))
                    import pandas as pd

                    reproduced = root / "split_manifest.csv"
                    pd.DataFrame({"row_id": frame.index, "partition": assigned}).to_csv(
                        reproduced, index=False
                    )
                    ok = sha256(reproduced) == split["sha256"]
                elif builtin == "inventory":
                    saved = json.loads(
                        (historical / "outputs" / step["outputs"][0]["name"]).read_text(encoding="utf-8")
                    )
                    ok = saved == {
                        "brief": state.brief,
                        "inventory": state.inventory,
                        **({"columns": state.columns} if state.columns else {}),
                    }
                else:
                    # Report contents are deterministic projections; integrity plus regenerate comparison.
                    ok = all(
                        (session.root / o["path"]).is_file()
                        and sha256(session.root / o["path"]) == o["sha256"]
                        for o in step["outputs"]
                    )
                results.append(
                    {
                        "step_id": step["step_id"],
                        "ok": ok,
                        "kind": "engine_operation",
                        "comparison": "split regeneration" if builtin == "split" else "evidence consistency",
                    }
                )
                continue
            environment_id = step.get("lock_sha256", state.lock_sha256)
            if environment_id not in environments:
                environment_root = root / "environments" / environment_id
                environment_root.mkdir(parents=True)
                snapshot = environment_root / "requirements.lock"
                snapshot.write_text(
                    "\n".join(step.get("environment_packages", state.environment_packages)) + "\n",
                    encoding="utf-8",
                )
                if sha256(snapshot) != environment_id:
                    raise IntegrityError("Recorded package snapshot does not match its hash")
                create(environment_root, [], frozen=snapshot, runtime_source=runtime_source)
                environments[environment_id] = environment_root
            environment_root = environments[environment_id]
            run = root / ".mlca/steps" / step["step_id"]
            run.mkdir(parents=True)
            (run / "outputs").mkdir()
            (run / "scratch").mkdir()
            shutil.copyfile(script, run / "script.py")
            original_inputs = json.loads((historical / "inputs.json").read_text(encoding="utf-8"))
            inputs = {}
            for name, entry in original_inputs.items():
                source = Path(entry["path"])
                if name == "test":
                    continue
                source = mapping.get(str(source), source)
                if sha256(source) != entry["sha256"]:
                    raise IntegrityError("Replay input hash changed")
                inputs[name] = {"path": str(source), "sha256": entry["sha256"]}
            action = session.workflow.actions.get(step["action_id"])
            reads_test = action.reads_test if action else step["event_id"] == "test"
            exposure = (
                exposed(session.root, state, step["step_id"], session.emit)
                if reads_test
                else nullcontext(None)
            )
            with exposure as test_path:
                if test_path:
                    inputs["test"] = {"path": str(test_path), "sha256": sha256(test_path)}
                atomic_json(run / "inputs.json", inputs)
                result = execute(
                    python(environment_root / ".mlca/env"),
                    run,
                    [Path(v["path"]) for v in inputs.values()],
                    environment_root / ".mlca/env",
                    environment_root / ".mlca/runtime",
                    session.root / ".mlca/style.mplstyle",
                    level,
                    action.timeout_s if action else 300,
                    state.split["train_index_sha256"] if state.split else "",
                    expected_train_rows=state.split["counts"]["train"] if state.split else 0,
                )
            differences = []
            for output in step["outputs"]:
                if output["name"] == "manifest.json":
                    if (run / "manifest.json").exists():
                        mapping[str(session.root / output["path"])] = run / "manifest.json"
                    continue
                reproduced = run / "outputs" / output["name"]
                if output["kind"] == "figure":
                    continue  # Rendering metadata is not a numerical reproducibility claim.
                if not reproduced.is_file() or sha256(reproduced) != output["sha256"]:
                    differences.append(output["name"])
                elif reproduced.exists():
                    mapping[str(session.root / output["path"])] = reproduced
            manifest = run / "manifest.json"
            metrics = (
                json.loads(manifest.read_text(encoding="utf-8")).get("metrics", [])
                if manifest.exists()
                else []
            )
            if metrics != step.get("metrics", []):
                differences.append("metrics")
            results.append(
                {
                    "step_id": step["step_id"],
                    "ok": result["exit_status"] == 0 and not differences,
                    "differences": differences,
                    "exit_status": result["exit_status"],
                    "figures_comparison": "metrics only",
                }
            )
    return {"ok": all(r["ok"] for r in results), "steps": results, "fresh_environment": True}
