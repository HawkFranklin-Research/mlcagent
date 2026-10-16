import sqlite3
from pathlib import Path

import pandas as pd

from mlca.privacy.rows import RowFingerprints
from mlca.project.inventory import read_table
from tests.unit.test_row_fingerprints import create_guard, materialize_v2


def test_legacy_read_write_never_silently_migrates(tmp_path):
    frame = pd.DataFrame({"a": [1.234567, 2.0, 3.0], "b": ["toy-a", "toy-b", "toy-c"]})
    guard, registered = create_guard(tmp_path / "legacy", frame)
    materialize_v2(guard)
    before = guard.path.read_bytes()
    reopened = RowFingerprints(guard.root).ensure(registered)
    assert reopened.path.read_bytes() == before
    reopened.register_split("second", frame, pd.Series(["train", "val", "test"]))
    with sqlite3.connect(guard.path) as db:
        assert db.execute("SELECT version FROM metadata").fetchone()[0] == 2
    assert reopened.contains_rows(frame.rename(columns=str.upper))


def test_normalized_queries_and_privacy_verdicts_match_legacy_with_bounded_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("mlca.privacy.rows.VALUE_CACHE_LIMIT", 8)
    frame = pd.DataFrame(
        {
            "a": [1.23456789, 8.87654321, None],
            "b": [12.3456789, 87.654321, 9.0],
            "c": ["toy-a", "toy-b", "toy-c"],
        }
    )
    old, registered = create_guard(tmp_path / "old", frame)
    materialize_v2(old)
    new, regnew = create_guard(tmp_path / "new", frame)
    with sqlite3.connect(old.path) as db:
        salt = db.execute("SELECT salt FROM metadata").fetchone()[0]
    new._salt = salt
    with sqlite3.connect(new.path) as db:
        db.execute("UPDATE metadata SET salt=?", (salt,))
        new._insert(
            db, "registered:source", read_table(Path(regnew[0]["original_path"])), regnew[0]["sha256"]
        )
    assignments = pd.Series(["train", "val", "test"])
    for guard in [old, new]:
        guard.register_split("split", frame, assignments)
    with sqlite3.connect(old.path) as a, sqlite3.connect(new.path) as b:
        for table, order in [("rows", "dataset,row_id"), ("cells", "dataset,row_id,column_name,precision")]:
            assert (
                a.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()
                == b.execute(f"SELECT * FROM {table} ORDER BY {order}").fetchall()
            )
    probes = [
        frame,
        frame.round(4).rename(columns=str.upper),
        frame[["a", "c"]],
        pd.DataFrame({"A": [1.23456789], "B": [87.654321], "C": ["toy-c"]}),
        pd.DataFrame({"summary": ["aggregate"], "count": [10000]}),
    ]
    for sample in probes:
        assert new.contains_rows(sample) == old.contains_rows(sample)
    for value in [frame.iloc[0].to_dict(), list(frame.iloc[0]), {"nested": [frame.iloc[0].to_dict()]}, 42]:
        assert new.contains_full_row(value) == old.contains_full_row(value)
    assert new.ensure(regnew).path == new.path


def test_repeated_fingerprints_are_smaller_without_losing_either_precision(tmp_path):
    frame = pd.DataFrame({f"feature_{i}": [j % 20 for j in range(300)] for i in range(16)})
    compact, _ = create_guard(tmp_path / "compact", frame)
    legacy, _ = create_guard(tmp_path / "legacy", frame)
    materialize_v2(legacy)
    with sqlite3.connect(legacy.path) as db:
        db.execute("VACUUM")
    assert compact.path.stat().st_size < legacy.path.stat().st_size * 0.5
    with sqlite3.connect(compact.path) as db:
        assert db.execute("SELECT count(*) FROM cells").fetchone()[0] == frame.size * 2
        assert db.execute("SELECT DISTINCT precision FROM cells ORDER BY precision").fetchall() == [
            (4,),
            (6,),
        ]
        assert db.execute("SELECT count(*) FROM digest_ids").fetchone()[0] < frame.size
