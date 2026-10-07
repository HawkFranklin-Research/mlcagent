import json
import math
from pathlib import Path
from typing import Any

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import sha256


def collect(root: Path, step: Path, action: Any, state: Any) -> dict:
    manifest_file = step / "manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding="utf-8")) if manifest_file.exists() else {}
    if not isinstance(manifest, dict):
        raise MlcaUserError("Runtime manifest must be an object")
    if any(path.is_symlink() for path in step.rglob("*")):
        raise IntegrityError("Step symlinks are not permitted")
    outputs, figures = [], []
    reported = {o["name"]: o for o in manifest.get("outputs", [])}
    declared = {o.name: o for o in action.outputs}
    for spec in action.outputs:
        if spec.required and not (step / "outputs" / spec.name).is_file():
            raise MlcaUserError(f"Required output missing: {spec.name}", category="missing_output")
    for path in sorted((step / "outputs").rglob("*")):
        if path.is_symlink():
            raise IntegrityError("Output symlinks are not permitted")
        if not path.is_file():
            continue
        name = str(path.relative_to(step / "outputs"))
        info = reported.get(name, {})
        kind = declared[name].kind if name in declared else info.get("kind", "other")
        entry = {
            "name": name,
            "path": str(path.relative_to(root)),
            "sha256": sha256(path),
            "size": path.stat().st_size,
            "kind": kind,
            "caption": info.get("caption", ""),
        }
        if kind == "table":
            from mlca.privacy.rows import guard

            matched = guard(root, state).file_contains_rows(path)
            entry["contains_data_rows"] = matched
            entry["row_privacy_checked"] = matched is not None
        outputs.append(entry)
        if kind == "figure":
            figures.append(entry)
    metrics = manifest.get("metrics", [])
    for metric in metrics:
        if metric["split"] not in {"train", "val", "test"} or not math.isfinite(float(metric["value"])):
            raise MlcaUserError("Invalid metric in runtime manifest")
        if metric["split"] == "test" and not action.reads_test:
            raise MlcaUserError("Test metric is not permitted for this action", category="test_lock")
    fits = manifest.get("fits", [])
    if action.event in {"preprocess", "features", "model"}:
        if not fits or any(
            f["partition"] != "train" or f["index_sha256"] != state.split["train_index_sha256"] for f in fits
        ):
            raise MlcaUserError("Missing or invalid frozen-training fit evidence", category="fit_rule")
    if any(o["kind"] == "model" for o in outputs) and action.event not in {"preprocess", "features", "model"}:
        raise MlcaUserError("Model artifacts may only be created in fitting stages")
    return {"outputs": outputs, "figures": figures, "metrics": metrics, "facts": manifest.get("facts", [])}


def freeze(step: Path) -> None:
    for path in step.rglob("*"):
        if not path.is_symlink():
            path.chmod(0o555 if path.is_dir() else 0o444)
    step.chmod(0o555)
