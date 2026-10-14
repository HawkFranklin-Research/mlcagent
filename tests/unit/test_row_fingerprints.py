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
    assert guard.contains_full_row(13.25)
    assert not guard.contains_full_row(1000)
    assert not guard.contains_rows(pd.DataFrame())


def test_corrupt_store_refused_without_returning_values(tmp_path):
    guard, registered = create_guard(tmp_path / "study", pd.DataFrame({"x": [987.123]}))
    guard.path.write_bytes(b"invalid database")
    with pytest.raises(IntegrityError, match="store is invalid"):
        guard.ensure(registered)


def test_unnamed_threshold_distinct_cells_and_precisions(tmp_path):
    frame = pd.DataFrame(
        {
            "a": [1.234567, 8.876543],
            "b": [12.34567, 87.65432],
            "c": [123.4567, 876.5432],
            "d": ["patient-a", "patient-b"],
        }
    )
    guard, _ = create_guard(tmp_path / "study", frame)
    assert guard.contains_rows(frame.rename(columns=str.upper))
    assert guard.contains_rows(frame.round(4).rename(columns=str.upper))
    coarse = frame.iloc[[0], :3].map(lambda v: float(f"{v:.4g}"))
    assert guard.contains_rows(coarse.rename(columns=str.upper))
    assert guard.contains_rows(coarse.assign(extra="different"))  # Three of four cells suffice.
    assert not guard.contains_rows(coarse.iloc[:, :2].assign(extra="different"))
    assert not guard.contains_rows(pd.DataFrame({"A": [1.234567], "B": [1.234567], "C": [1.234567]}))
    assert not guard.contains_rows(pd.DataFrame({"A": [1.234567], "B": [87.65432], "C": [123.4567]}))
    assert guard.contains_full_row(frame.iloc[0].rename(str.upper).to_dict())
    fact = {key.upper(): float(f"{v:.4g}") if isinstance(v, float) else v for key, v in frame.iloc[0].items()}
    assert guard.contains_full_row(fact)
    with sqlite3.connect(guard.path) as db:
        assert db.execute("SELECT DISTINCT precision FROM cells ORDER BY precision").fetchall() == [
            (4,),
            (6,),
        ]


def downgrade_to_v1(guard):
    with sqlite3.connect(guard.path) as db:
        db.executescript("""
            DROP INDEX cell_lookup;
            ALTER TABLE cells RENAME TO new_cells;
            CREATE TABLE cells (dataset TEXT, row_id INTEGER, column_name TEXT, digest TEXT,
                PRIMARY KEY(dataset,row_id,column_name));
            INSERT INTO cells SELECT dataset,row_id,column_name,digest FROM new_cells WHERE precision=6;
            DROP TABLE new_cells;
            CREATE INDEX cell_lookup ON cells(dataset,column_name,digest,row_id);
            UPDATE metadata SET version=1;
        """)


def test_v1_migration_and_failed_migration_preserves_index(tmp_path):
    frame = pd.DataFrame({"a": [1.234567], "b": [12.34567], "c": [123.4567]})
    guard, registered = create_guard(tmp_path / "study", frame)
    downgrade_to_v1(guard)
    old = guard.path.read_bytes()
    source = registered[0]["original_path"]
    frame.assign(a=99).to_csv(source, index=False)
    with pytest.raises(IntegrityError, match="unchanged registered"):
        guard.ensure(registered)
    assert guard.path.read_bytes() == old
    frame.to_csv(source, index=False)
    guard.ensure(registered)
    with sqlite3.connect(guard.path) as db:
        assert db.execute("SELECT version FROM metadata").fetchone()[0] == 2
    assert guard.contains_rows(frame.round(4).rename(columns=str.upper))


def test_cell_lookup_uses_full_index_and_preserves_matches(tmp_path):
    from mlca.privacy.rows import _CELL_MATCH_SQL

    frame = pd.DataFrame({"a": [1.234567, 0.0], "b": [0.0, 1.234567], "c": ["yes", "no"]})
    guard, _ = create_guard(tmp_path / "study", frame)
    old = (
        "SELECT row_id, column_name FROM cells WHERE dataset=? AND "
        "((precision=6 AND digest=?) OR (precision=4 AND digest=?))"
    )
    with sqlite3.connect(guard.path) as db:
        for value in [0.0, 1.234567, 1.235, "yes", "absent"]:
            d6, d4 = guard._digest(value, 6), guard._digest(value, 4)
            assert sorted(db.execute(old, ("registered:source", d6, d4))) == sorted(
                db.execute(_CELL_MATCH_SQL, ("registered:source", d6, "registered:source", d4))
            )
        plan = [
            r[3]
            for r in db.execute(
                "EXPLAIN QUERY PLAN " + _CELL_MATCH_SQL,
                ("registered:source", "a", "registered:source", "b"),
            )
        ]
        assert sum("dataset=? AND precision=? AND digest=?" in detail for detail in plan) == 2


def test_json_table_and_records_are_checked_equally(tmp_path):
    import json

    from mlca.errors import MlcaUserError

    frame = pd.DataFrame({"a": [1.234567, 8.876543], "b": [12.34567, 87.65432], "c": [123.4567, 876.5432]})
    guard, _ = create_guard(tmp_path / "study", frame)
    path = tmp_path / "table.json"
    for orient in ["table", "records"]:
        frame.round(4).rename(columns=str.upper).to_json(path, orient=orient)
        assert guard.file_contains_rows(path)
    path.write_text(json.dumps([{"name": "aggregate", "count": 200, "mean": 54.321}]))
    assert not guard.file_contains_rows(path)
    path.write_text(json.dumps({"arbitrary": [1, 2, 3]}))
    with pytest.raises(MlcaUserError, match="Table JSON must"):
        guard.file_contains_rows(path)
