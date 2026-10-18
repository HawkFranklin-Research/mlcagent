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


def group_time_partitions(frame, params):
    """Split chronological components without separating a group or equal timestamp."""
    group, times = params["group_column"], params["time_columns"]
    if not times or not {group, *times} <= set(frame.columns) or frame[[group, *times]].isna().any().any():
        raise MlcaUserError("Joint group/time split requires complete declared grouping and time columns")
    keys = pd.Series(list(map(tuple, frame[times].itertuples(index=False, name=None))), index=frame.index)
    bounds = []
    for value, rows in frame.groupby(group, sort=False, observed=True):
        span = keys.loc[rows.index]
        bounds.append((min(span), max(span), value, len(rows)))
    # Overlapping group intervals (including ties) must remain in one component.
    components = []
    for start, end, value, count in sorted(bounds, key=lambda item: item[0]):
        if not components or start > components[-1][0]:
            components.append([end, [value], count])
        else:
            components[-1][0] = max(end, components[-1][0])
            components[-1][1].append(value)
            components[-1][2] += count
    if len(components) < 3:
        raise MlcaUserError(
            "Declared groups and time intervals cannot form three disjoint chronological partitions",
            category="gate_blocked",
        )
    totals = np.cumsum([c[2] for c in components])
    a = min(
        range(1, len(components) - 1),
        key=lambda i: abs(totals[i - 1] - len(frame) * params["train_fraction"]),
    )
    b = min(
        range(a + 1, len(components)),
        key=lambda i: abs(totals[i - 1] - len(frame) * (params["train_fraction"] + params["val_fraction"])),
    )
    labels = {}
    for i, (_, groups, _) in enumerate(components):
        label = "train" if i < a else "val" if i < b else "test"
        labels.update((value, label) for value in groups)
    return frame[group].map(labels).astype("object")


def time_block_partitions(times, train, val):
    """Chronological split whose boundaries fall only between distinct timestamps."""
    order = {value: rank for rank, value in enumerate(sorted(set(times)))}
    if len(order) < 3:
        raise MlcaUserError("Time split needs at least three distinct timestamps")
    codes = np.array([order[value] for value in times])
    totals = np.cumsum(np.bincount(codes))
    n = len(times)
    a = min(range(1, len(order) - 1), key=lambda i: abs(totals[i - 1] - n * train))
    b = min(range(a + 1, len(order)), key=lambda i: abs(totals[i - 1] - n * (train + val)))
    labels = np.where(codes < a, "train", np.where(codes < b, "val", "test"))
    return pd.Series(labels, index=times.index, dtype="object")


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
    elif method == "group_time":
        assignments = group_time_partitions(frame, params)
    elif method == "time":
        column = params.get("time_column", "")
        if column not in frame or frame[column].isna().any():
            raise MlcaUserError("Time split requires a complete time column")
        ordered = frame.sort_values(column, kind="stable")
        assign(ordered.index)
        # Equal timestamps must not span partitions: move each boundary to the nearest
        # timestamp change instead of refusing the requested fractions.
        if (
            pd.DataFrame({"time": frame[column], "partition": assignments})
            .groupby("time")
            .partition.nunique()
            .max()
            > 1
        ):
            assignments = time_block_partitions(frame[column], train, val)
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
    if state.group_column and state.task.get("time_columns"):
        params = {
            **params,
            "method": "group_time",
            "group_column": state.group_column,
            "time_columns": state.task["time_columns"],
        }
        assignments = partitions(frame, params, target)
    elif state.group_column:
        params = {**params, "method": "group", "group_column": state.group_column}
        assignments = partitions(frame, params, target)
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
