import sqlite3

import numpy as np
import pandas as pd
import pytest

from mlca.errors import IntegrityError
from mlca.paths import sha256
from mlca.privacy.rows import RowFingerprints


def create_guard(root, frame):
    root.mkdir()
    source = root / "source.csv"
    frame.to_csv(source, index=False)
    registered = [{"name": "source", "original_path": str(source), "sha256": sha256(source)}]
    return RowFingerprints(root).ensure(registered), registered


def test_projection_order_rounding_nulls_and_fact_shapes(tmp_path):
    frame = pd.DataFrame(
        {"z": [1.23456789, 9.87654321, np.nan], "name": ["one", "two", "three"], "label": [1, 0, 1]}
    )
    guard, registered = create_guard(tmp_path / "study", frame)
    assert guard.contains_rows(frame.iloc[[0]][["name", "z"]].round(5).assign(extra="ignored"))
    assert guard.contains_rows(frame.iloc[[2]][["z", "name"]])
    assert not guard.contains_rows(pd.DataFrame({"z": [42.125], "name": ["aggregate"]}))
    # Matching cells must belong to the same source row, not merely exist somewhere.
    assert not guard.contains_rows(pd.DataFrame({"z": [frame.z[0]], "name": ["two"]}))
    row = frame.iloc[0].to_dict()
    assert guard.contains_full_row(row)
    assert guard.contains_full_row({"records": [row]})
    assert guard.contains_full_row(list(row.values()))
    assert not guard.contains_full_row({"name": "one"})
    assert not guard.contains_full_row(3)
    assert guard.ensure(registered).path == guard.path
    assert not guard.path.stat().st_mode & 0o077


def test_salt_split_profiles_and_fail_closed(tmp_path):
    frame = pd.DataFrame({"a": [1.125, 2.25, 3.375], "b": ["ROW_CANARY_A", "ROW_CANARY_B", "ROW_CANARY_C"]})
    left, registered = create_guard(tmp_path / "left", frame)
    right, _ = create_guard(tmp_path / "right", frame)
    assignments = pd.Series(["train", "val", "test"])
    left.register_split("split-id", frame, assignments)
    with sqlite3.connect(left.path) as db:
        assert db.execute("SELECT count(*) FROM datasets").fetchone()[0] == 4
        first_hash = db.execute(
            "SELECT digest FROM rows WHERE dataset='registered:source' AND row_id=0"
        ).fetchone()[0]
    with sqlite3.connect(right.path) as db:
        assert first_hash != db.execute("SELECT digest FROM rows WHERE row_id=0").fetchone()[0]
    assert b"ROW_CANARY" not in left.path.read_bytes()
    left.path.unlink()
    source = registered[0]["original_path"]
    pd.DataFrame({"a": [0]}).to_csv(source, index=False)
    with pytest.raises(IntegrityError, match="unchanged registered"):
        left.ensure(registered)
    assert not left.path.exists()


def test_single_column_and_empty_table(tmp_path):
    guard, _ = create_guard(tmp_path / "study", pd.DataFrame({"feature": [13.251, 42.825]}))
    assert guard.contains_full_row(13.251)
    assert not guard.contains_full_row(1000)
    assert not guard.contains_rows(pd.DataFrame())


def test_corrupt_store_refused_without_returning_values(tmp_path):
    guard, registered = create_guard(tmp_path / "study", pd.DataFrame({"x": [987.123]}))
    guard.path.write_bytes(b"invalid database")
    with pytest.raises(IntegrityError, match="store is invalid"):
        guard.ensure(registered)
