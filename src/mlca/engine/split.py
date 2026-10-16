import hashlib
import io
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import sha256
from mlca.project.init import column_for, primary_for
from mlca.project.inventory import read_table
from mlca.sandbox.vault import seal


def partitions(frame: Any, params: Any, target: str) -> Any:
    train, val = float(params["train_fraction"]), float(params["val_fraction"])
    if train <= 0 or val <= 0 or train + val >= 1:
        raise MlcaUserError("Training and validation fractions must be positive and leave a test partition")
    method, seed = params["method"], int(params["seed"])
    rng = np.random.default_rng(seed)
    assignments = pd.Series("", index=frame.index, dtype="object")

    def assign(index: Any) -> Any:
        index = np.asarray(index)
        n_train, n_val = int(len(index) * train), int(len(index) * val)
        if min(n_train, n_val, len(index) - n_train - n_val) < 1:
            raise MlcaUserError("Too few rows in a stratum for three nonempty partitions")
        assignments.loc[index[:n_train]] = "train"
        assignments.loc[index[n_train : n_train + n_val]] = "val"
        assignments.loc[index[n_train + n_val :]] = "test"

    if method == "stratified":
        if target not in frame or frame[target].isna().any():
            raise MlcaUserError("Stratified split requires a complete target column")
        for _, group in frame.groupby(target, sort=True):
            assign(rng.permutation(group.index))
    elif method == "group":
        column = params.get("group_column", "")
        if column not in frame or frame[column].isna().any():
            raise MlcaUserError("Group split requires a complete group column")
        groups = rng.permutation(frame[column].unique())
        if len(groups) < 3:
            raise MlcaUserError("Group split needs at least three groups")
        a = max(1, min(len(groups) - 2, int(len(groups) * train)))
        b = max(a + 1, min(len(groups) - 1, a + int(len(groups) * val)))
        for label, selected in zip(["train", "val", "test"], [groups[:a], groups[a:b], groups[b:]]):
            assignments.loc[frame[column].isin(selected)] = label
    elif method == "time":
        column = params.get("time_column", "")
        if column not in frame or frame[column].isna().any():
            raise MlcaUserError("Time split requires a complete time column")
        ordered = frame.sort_values(column, kind="stable")
        assign(ordered.index)
        # Equal timestamps must not span partitions.
        if (
            pd.DataFrame({"time": frame[column], "partition": assignments})
            .groupby("time")
            .partition.nunique()
            .max()
            > 1
        ):
            raise MlcaUserError("Time boundaries split equal timestamps; choose different fractions")
    elif method == "random":
        assign(rng.permutation(frame.index))
    else:
        raise MlcaUserError("Unknown split method")
    return assignments


def freeze(root: Path, state: Any, params: dict, step_id: str, emit: Any) -> dict:
    if state.split:
        raise MlcaUserError(
            "This branch already has a frozen split; branch before split to change the protocol"
        )
    registered = state.data[primary_for(state)]
    path = Path(registered["original_path"])
    if sha256(path) != registered["sha256"]:
        raise IntegrityError("Registered input changed")
    if state.prepared_data:
        path = root / state.prepared_data["path"]
        if sha256(path) != state.prepared_data["sha256"]:
            raise IntegrityError("Prepared input changed")
    frame = read_table(path)
    if not state.task.get("autonomous"):
        frame = frame.reset_index(drop=True)
    if not frame.index.is_unique:
        raise MlcaUserError("Row identifiers must be unique before freezing partitions")
    target = column_for(state) if state.template_id not in {"clustering", "representation"} else ""
    if state.group_column:
        params = {**params, "method": "group", "group_column": state.group_column}
    elif state.task.get("time_columns"):
        time_columns = state.task["time_columns"]
        # Lexicographic time tuple; use a private temporary sort key without changing data columns.
        frame = frame.copy()
        key = "__mlca_time_order__"
        if key in frame:
            raise MlcaUserError("Reserved time ordering name conflicts with data")
        frame[key] = list(map(tuple, frame[time_columns].itertuples(index=False, name=None)))
        assignments = partitions(frame, {**params, "method": "time", "time_column": key}, target)
        frame = frame.drop(columns=[key])
        params = {**params, "method": "time", "time_columns": time_columns}
    else:
        assignments = None
    if state.group_column or not state.task.get("time_columns"):
        assignments = partitions(frame, params, target)
    # Retain group values for train-only internal folds; protocol excludes them from features.
    from mlca.privacy.rows import guard

    guard(root, state).register_split(step_id, frame, assignments)
    directory = root / ".mlca/data/splits" / step_id
    directory.mkdir(parents=True, exist_ok=False)
    manifest = directory / "split_manifest.csv"
    pd.DataFrame({"row_id": frame.index, "partition": assignments}).to_csv(manifest, index=False)
    for name in ["train", "val"]:
        frame.loc[assignments == name].to_parquet(directory / f"{name}.parquet", index=True)
    buffer = io.BytesIO()
    frame.loc[assignments == "test"].to_parquet(buffer, index=True)
    vault = root / ".mlca/vault" / f"{step_id}.enc"
    seal(state.project_id, step_id, buffer.getvalue(), vault)
    train_index = frame.loc[assignments == "train"].index.tolist()
    payload = {
        "split_id": step_id,
        "primary_data": primary_for(state),
        "parameters": params,
        "sha256": sha256(manifest),
        "test_plain_sha256": hashlib.sha256(buffer.getvalue()).hexdigest(),
        "train_index_sha256": hashlib.sha256(
            json.dumps(train_index, default=str, separators=(",", ":")).encode()
        ).hexdigest(),
        "counts": assignments.value_counts().to_dict(),
    }
    for name, file in [
        ("manifest", manifest),
        ("train", directory / "train.parquet"),
        ("val", directory / "val.parquet"),
        ("vault", vault),
    ]:
        payload[name] = {"path": str(file.relative_to(root)), "sha256": sha256(file)}
    emit("SplitFrozen", payload)
    return payload
