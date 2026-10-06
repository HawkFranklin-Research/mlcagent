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
    return {
        "name": name,
        "rows": len(frame),
        "columns": list(frame.columns),
        "dtypes": {str(c): str(t) for c, t in frame.dtypes.items()},
        "missing": {str(c): int(v) for c, v in frame.isna().sum().items()},
        "sha256": sha256(path),
        "size": path.stat().st_size,
    }
