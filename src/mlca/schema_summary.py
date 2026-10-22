"""Bounded, value-aware schema summaries for model-facing inventory views."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import pandas as pd

FULL_SCHEMA_LIMIT = 200
LOW_CARDINALITY_LIMIT = 20


def finite_bounds(values):
    values = [v for v in (scalar(v) for v in values) if v is not None]
    return [min(values), max(values)] if values else [None, None]


def scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, (str, int, float, bool)):
        return value if not isinstance(value, float) or math.isfinite(value) else None
    return str(value)


def value_information(series: pd.Series) -> dict[str, Any]:
    if series.nunique(dropna=False) <= LOW_CARDINALITY_LIMIT:
        return {
            "value_counts": [
                {"value": scalar(value), "count": int(count)}
                for value, count in series.value_counts(dropna=False).items()
            ]
        }
    if pd.api.types.is_numeric_dtype(series):
        return {
            "numeric_summary": {
                "min": scalar(series.min()),
                "max": scalar(series.max()),
                "mean": scalar(series.mean()),
                "quantiles": {str(q): scalar(series.quantile(q)) for q in [0.25, 0.5, 0.75]},
            }
        }
    return {"numeric_summary": None, "summary_status": "non_numeric_high_cardinality"}


def summarize_frame(frame: pd.DataFrame, *, name: str, brief: str = "") -> dict[str, Any]:
    """Return a complete schema for small tables and a bounded schema for wide tables.

    Omitted high-cardinality numeric columns remain available to local proposal validation.
    """
    columns = list(frame.columns)
    if len(columns) <= FULL_SCHEMA_LIMIT:
        chosen = columns
        blocks: list[dict[str, Any]] = []
    else:
        named = {str(c) for c in columns if str(c) and str(c) in brief}
        chosen = []
        numeric_groups: dict[str, list[tuple[str, pd.Series]]] = defaultdict(list)
        for index, column in enumerate(columns):
            series = frame[column]
            dtype = str(series.dtype)
            keep = (
                not pd.api.types.is_numeric_dtype(series)
                or series.nunique(dropna=False) <= LOW_CARDINALITY_LIMIT
                or str(column) in named
                or index < 20
                or index >= len(columns) - 20
            )
            if keep:
                chosen.append(column)
            elif pd.api.types.is_numeric_dtype(series):
                numeric_groups[dtype].append((str(column), series))

        blocks = []
        for dtype, entries in sorted(numeric_groups.items()):
            group = [series for _, series in entries]
            minima = [s.min() for s in group]
            maxima = [s.max() for s in group]
            means = [s.mean() for s in group]
            blocks.append(
                {
                    "dtype": dtype,
                    "column_count": len(group),
                    "missing_values": int(sum(s.isna().sum() for s in group)),
                    "columns_with_missing": sum(bool(s.isna().any()) for s in group),
                    "min_range": [*finite_bounds(minima)],
                    "max_range": [*finite_bounds(maxima)],
                    "mean_range": [*finite_bounds(means)],
                    "example_names": [name for name, _ in entries[:20]],
                }
            )

    return {
        "name": name,
        "rows": len(frame),
        "total_columns": len(columns),
        "columns": [
            {
                "name": str(c),
                "dtype": str(frame[c].dtype),
                "unique": int(frame[c].nunique(dropna=False)),
                "missing": int(frame[c].isna().sum()),
                **value_information(frame[c]),
            }
            for c in chosen
        ],
        "numeric_blocks": blocks,
        "columns_omitted": len(columns) - len(chosen),
    }


def summarize_inventory(item: dict[str, Any], *, brief: str = "") -> dict[str, Any]:
    """Bound a registered inventory record for display to a model."""
    columns = item.get("columns", [])
    if len(columns) <= FULL_SCHEMA_LIMIT:
        return item
    dtypes = item.get("dtypes", {})
    missing = item.get("missing", {})
    unique = item.get("unique", {})
    summaries = item.get("column_summaries", {})
    named = {str(c) for c in columns if str(c) and str(c) in brief}
    chosen = []
    groups: dict[str, list[str]] = defaultdict(list)
    for index, column in enumerate(columns):
        dtype = str(dtypes.get(column, "unknown"))
        low = unique.get(column, FULL_SCHEMA_LIMIT + 1) <= LOW_CARDINALITY_LIMIT
        try:
            numeric = pd.api.types.is_numeric_dtype(pd.api.types.pandas_dtype(dtype))
        except TypeError:
            numeric = False
        if not numeric or low or column in named or index < 20 or index >= len(columns) - 20:
            chosen.append(column)
        else:
            groups[dtype].append(column)
    blocks = []
    for dtype, names in sorted(groups.items()):
        details = [summaries.get(n, {}) for n in names]

        def bounds(key):
            return finite_bounds([d.get(key) for d in details])

        blocks.append(
            {
                "dtype": dtype,
                "column_count": len(names),
                "missing_values": sum(int(missing.get(n, 0)) for n in names),
                "columns_with_missing": sum(bool(missing.get(n, 0)) for n in names),
                "min_range": bounds("min"),
                "max_range": bounds("max"),
                "mean_range": bounds("mean"),
                "example_names": names[:20],
            }
        )
    return {
        "name": item.get("name"),
        "rows": item.get("rows"),
        "total_columns": len(columns),
        "columns": [
            {
                "name": c,
                "dtype": dtypes.get(c),
                "unique": unique.get(c),
                "missing": missing.get(c),
                **summaries.get(c, {}),
            }
            for c in chosen
        ],
        "numeric_blocks": blocks,
        "columns_omitted": len(columns) - len(chosen),
    }


def model_view(value):
    """Bound model-only schema collections; never modify execution state or scripts.

    Wide maps/lists are explicitly abbreviated. The complete schema and protocol
    remain on disk and available through declared runtime inputs.
    """
    if isinstance(value, dict):
        if "numeric_blocks" in value and "total_columns" in value:
            return value  # Required detailed label/non-numeric columns must remain visible.
        if isinstance(value.get("columns"), list) and isinstance(value.get("dtypes"), dict):
            return summarize_inventory(value)
        if len(value) > FULL_SCHEMA_LIMIT:
            keys = list(value)
            selected = keys[:20] + keys[-20:]
            return {
                "total_entries": len(value),
                "omitted_entries": len(value) - len(selected),
                "examples": {k: model_view(value[k]) for k in selected},
                "note": "Abbreviated model context; read declared inputs for the complete schema.",
            }
        return {key: model_view(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        if len(value) > FULL_SCHEMA_LIMIT:
            return {
                "total_entries": len(value),
                "omitted_entries": len(value) - 40,
                "examples": [model_view(v) for v in [*value[:20], *value[-20:]]],
                "note": "Abbreviated model context; read declared inputs for the complete schema.",
            }
        return [model_view(v) for v in value]
    return value
