"""Private salted fingerprints for exact and simple, name-independent row copies."""

import hashlib
import hmac
import json
import math
import numbers
import os
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

import pandas as pd
from filelock import FileLock

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import canonical, sha256
from mlca.project.inventory import read_table


def normalized(value, precision=6):
    if value is None or (pd.api.types.is_scalar(value) and pd.isna(value)):
        return ["missing"]
    if isinstance(value, numbers.Number):
        number = float(value)
        if math.isfinite(number):
            return ["number", format(number if number else 0, f".{precision}g")]
        return ["number", str(number)]
    if hasattr(value, "isoformat"):
        return ["text", value.isoformat()]
    if isinstance(value, bytes):
        return ["bytes", value.hex()]
    return ["text", str(value)]


class RowFingerprints:
    def __init__(self, root):
        self.root = Path(root)
        self.directory = self.root / ".mlca/private"
        self.path = self.directory / "row_fingerprints"
        self._salt = None

    def _connect(self, versions=(2,)):
        if self.directory.is_symlink() or self.path.is_symlink() or not self.path.is_file():
            raise IntegrityError(
                "Private row fingerprints unavailable; rebuild with unchanged registered data"
            )
        db = None
        try:
            db = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True)
            version, salt = db.execute("SELECT version, salt FROM metadata").fetchone()
            if version not in versions or len(salt) != 32:
                raise ValueError()
            self._salt = salt
            return db
        except (sqlite3.Error, ValueError, TypeError):
            if db is not None:
                db.close()
            raise IntegrityError("Private row fingerprint store is invalid") from None

    def _digest(self, value, precision=6):
        return hmac.new(
            self._salt, canonical(normalized(value, precision)).encode(), hashlib.sha256
        ).hexdigest()

    def _insert(self, db, name, frame, digest):
        columns = [str(c) for c in frame.columns]
        if len(set(columns)) != len(columns):
            raise MlcaUserError("Row fingerprints require unique column names")
        db.execute("DELETE FROM cells WHERE dataset=?", (name,))
        db.execute("DELETE FROM rows WHERE dataset=?", (name,))
        db.execute("INSERT OR REPLACE INTO datasets VALUES (?,?,?)", (name, canonical(columns), digest))
        ordered = sorted(range(len(columns)), key=lambda i: columns[i])
        for row_id, row in enumerate(frame.itertuples(index=False, name=None)):
            cells = [self._digest(value) for value in row]
            full = hmac.new(
                self._salt, canonical([[columns[i], cells[i]] for i in ordered]).encode(), hashlib.sha256
            ).hexdigest()
            db.execute("INSERT INTO rows VALUES (?,?,?)", (name, row_id, full))
            db.executemany(
                "INSERT INTO cells VALUES (?,?,?,?,?)",
                (
                    (name, row_id, col, precision, self._digest(value, precision))
                    for col, value in zip(columns, row)
                    for precision in (6, 4)
                ),
            )

    def ensure(self, registered):
        """Build/migrate once, from registered source files whose hashes still match."""
        if self.directory.is_symlink():
            raise IntegrityError("Private row fingerprint directory must not be a symlink")
        self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.directory.chmod(0o700)
        with FileLock(str(self.directory / "row_fingerprints.lock")):
            expected = {"registered:" + item["name"]: item["sha256"] for item in registered}
            if self.path.exists():
                with closing(self._connect(versions=(1, 2))) as db:
                    stored = dict(
                        db.execute("SELECT name, source_sha256 FROM datasets WHERE name LIKE 'registered:%'")
                    )
                    if stored != expected:
                        raise IntegrityError("Private row fingerprints disagree with registered inputs")
                    if db.execute("SELECT version FROM metadata").fetchone()[0] == 2:
                        return self
                # V1 hashes cannot be reduced to four digits. Rebuild atomically from verified
                # registered rows, which already cover every historical split; never unseal test.
            fd, temporary = tempfile.mkstemp(prefix=".row-fingerprints-", dir=self.directory)
            os.close(fd)
            try:
                with closing(sqlite3.connect(temporary)) as db:
                    db.executescript("""
                        CREATE TABLE metadata (version INTEGER, salt BLOB);
                        CREATE TABLE datasets (name TEXT PRIMARY KEY, columns TEXT, source_sha256 TEXT);
                        CREATE TABLE rows (dataset TEXT, row_id INTEGER, digest TEXT, PRIMARY KEY(dataset,row_id));
                        CREATE TABLE cells (dataset TEXT, row_id INTEGER, column_name TEXT, precision INTEGER, digest TEXT,
                            PRIMARY KEY(dataset,row_id,column_name,precision));
                        CREATE INDEX cell_lookup ON cells(dataset,precision,digest,row_id,column_name);
                    """)
                    self._salt = os.urandom(32)
                    db.execute("INSERT INTO metadata VALUES (?,?)", (2, self._salt))
                    for item in registered:
                        file = Path(item["original_path"])
                        if not file.is_file() or sha256(file) != item["sha256"]:
                            raise IntegrityError(
                                "Cannot build row fingerprints without unchanged registered data"
                            )
                        self._insert(db, "registered:" + item["name"], read_table(file), item["sha256"])
                    db.commit()
                Path(temporary).chmod(0o600)
                os.replace(temporary, self.path)
            finally:
                Path(temporary).unlink(missing_ok=True)
        return self

    def register_split(self, split_id, frame, assignments):
        with FileLock(str(self.directory / "row_fingerprints.lock")):
            with closing(self._connect()):
                pass
            with closing(sqlite3.connect(self.path)) as db:
                for partition in ("train", "val", "test"):
                    self._insert(
                        db, f"split:{split_id}:{partition}", frame.loc[assignments == partition], None
                    )
                db.commit()

    def _match(self, db, dataset, columns, values):
        possible = None
        for column, value in zip(columns, values):
            matched = {
                row[0]
                for row in db.execute(
                    "SELECT row_id FROM cells WHERE dataset=? AND column_name=? AND precision=6 AND digest=?",
                    (dataset, column, self._digest(value)),
                )
            }
            possible = matched if possible is None else possible & matched
            if not possible:
                return False
        return bool(possible)

    def _match_values(self, db, dataset, values, required):
        """Count distinct returned cells matched to distinct cells in one source row."""
        candidates = {}
        for position, value in enumerate(values):
            for row_id, column in db.execute(
                "SELECT row_id, column_name FROM cells WHERE dataset=? AND "
                "((precision=6 AND digest=?) OR (precision=4 AND digest=?))",
                (dataset, self._digest(value, 6), self._digest(value, 4)),
            ):
                candidates.setdefault(row_id, {}).setdefault(position, set()).add(column)
        for edges in candidates.values():
            if len(edges) < required:
                continue
            owners = {}

            def assign(position, seen):
                for column in edges[position]:
                    if column in seen:
                        continue
                    seen.add(column)
                    if column not in owners or assign(owners[column], seen):
                        owners[column] = position
                        return True
                return False

            count = 0
            for position in edges:
                count += assign(position, set())
                if count >= required:
                    return True
        return False

    def contains_rows(self, frame):
        if frame.empty:
            return False
        with closing(self._connect()) as db:
            for name, saved in db.execute("SELECT name, columns FROM datasets"):
                shared = sorted(set(json.loads(saved)) & set(frame.columns))
                if shared and any(
                    self._match(db, name, shared, row)
                    for row in frame[shared].itertuples(index=False, name=None)
                ):
                    return True
                if any(
                    self._match_values(db, name, row, min(3, len(frame.columns)))
                    for row in frame.itertuples(index=False, name=None)
                ):
                    return True
        return False

    def contains_full_row(self, value):
        with closing(self._connect()) as db:
            schemas = [
                (name, json.loads(columns))
                for name, columns in db.execute("SELECT name, columns FROM datasets")
            ]

            def visit(item):
                for name, columns in schemas:
                    # Facts retain the full-row requirement, but names/order no longer matter.
                    values = list(item.values()) if isinstance(item, dict) else item
                    if isinstance(values, (list, tuple)) and len(values) >= len(columns):
                        scalars = [v for v in values if not isinstance(v, (dict, list, tuple))]
                        if len(scalars) >= len(columns) and self._match_values(
                            db, name, scalars, len(columns)
                        ):
                            return True
                    if isinstance(item, dict) and set(columns) <= set(item):
                        ordered = sorted(columns)
                        if self._match(db, name, ordered, [item[c] for c in ordered]):
                            return True
                    elif (
                        isinstance(item, (list, tuple))
                        and len(item) == len(columns)
                        and not any(isinstance(v, (dict, list, tuple)) for v in item)
                    ):
                        if self._match(db, name, columns, item) or self._match(
                            db, name, sorted(columns), item
                        ):
                            return True
                    elif len(columns) == 1 and not isinstance(item, (dict, list, tuple)):
                        if self._match_values(db, name, [item], 1):
                            return True
                if isinstance(item, dict):
                    return any(visit(v) for v in item.values() if isinstance(v, (dict, list, tuple)))
                if isinstance(item, (list, tuple)):
                    return any(visit(v) for v in item if isinstance(v, (dict, list, tuple)))
                return False

            return visit(value)

    def file_contains_rows(self, path):
        path = Path(path)
        if path.suffix.lower() in {".csv", ".tsv"}:
            frames = pd.read_csv(path, sep="\t" if path.suffix.lower() == ".tsv" else ",", chunksize=10000)
        elif path.suffix.lower() in {".parquet", ".pq"}:
            import pyarrow.parquet as parquet

            frames = (batch.to_pandas() for batch in parquet.ParquetFile(path).iter_batches(batch_size=10000))
        elif path.suffix.lower() == ".json":
            frames = [pd.read_json(path, orient="table")]
        else:
            return None
        return any(self.contains_rows(frame) for frame in frames)


def guard(root, state):
    return RowFingerprints(root).ensure(list(state.data.values()))
