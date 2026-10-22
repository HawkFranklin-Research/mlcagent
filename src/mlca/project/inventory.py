from pathlib import Path
from typing import Any

import pandas as pd

from mlca.errors import MlcaUserError
from mlca.paths import sha256


def read_table(path: Path) -> Any:
    if path.suffix.lower() in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    if path.suffix.lower() in {".csv", ".tsv"}:
        return pd.read_csv(path, sep="\t" if path.suffix.lower() == ".tsv" else ",")
    raise MlcaUserError("Supported input formats: CSV, TSV and Parquet")


def scan(name: str, path: Path) -> dict:
    frame = read_table(path)
    result = {
        "name": name,
        "rows": len(frame),
        "columns": list(frame.columns),
        "dtypes": {str(c): str(t) for c, t in frame.dtypes.items()},
        "missing": {str(c): int(v) for c, v in frame.isna().sum().items()},
        "sha256": sha256(path),
        "size": path.stat().st_size,
    }

    # Full local metadata supports schema views without rereading source data at each turn.
    if len(frame.columns) > 200:
        from mlca.schema_summary import scalar

        result["unique"] = {str(c): int(frame[c].nunique(dropna=False)) for c in frame}
        result["column_summaries"] = {
            str(c): {
                "min": scalar(frame[c].min()),
                "max": scalar(frame[c].max()),
                "mean": scalar(frame[c].mean()),
            }
            for c in frame
            if pd.api.types.is_numeric_dtype(frame[c])
        }
    return result


def table_columns(path: Path) -> list[str]:
    """Schema-only preview for selectors; never sends sample rows to a provider."""
    if path.suffix.lower() in {".parquet", ".pq"}:
        import pyarrow.parquet as pq

        return pq.ParquetFile(path).schema_arrow.names
    if path.suffix.lower() in {".csv", ".tsv"}:
        return list(pd.read_csv(path, sep="\t" if path.suffix.lower() == ".tsv" else ",", nrows=0).columns)
    raise MlcaUserError("Supported input formats: CSV, TSV and Parquet")
