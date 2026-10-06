import hashlib
import json
import os
from pathlib import Path
from typing import Any

from filelock import FileLock

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import atomic_json, canonical

from .schema import Record


class Store:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.path = root / ".mlca/log/events.jsonl"
        self.anchor = root / ".mlca/log/head.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = FileLock(str(self.path) + ".lock")
        self.callbacks = []
        self._records = []
        self._offset = 0
        self._digest = ""
        self._ids = set()
        self._heads = {}
        self._loaded = False
        self._signature = None

    def _parse(self, raw: bytes, line_number: int, previous: str, ids: set) -> Record:
        try:
            if not raw.endswith(b"\n"):
                raise ValueError("Incomplete append")
            record = Record.model_validate_json(raw)
        except Exception as exc:
            raise IntegrityError(f"Event log integrity failure at line {line_number}") from exc
        if record.prev_hash != previous:
            raise IntegrityError(
                f"line {line_number - 1} was modified (its hash no longer matches line {line_number})"
            )
        if record.id in ids or (record.parent_id is not None and record.parent_id not in ids):
            raise IntegrityError(
                f"Event log integrity failure at line {line_number}: duplicate id or unknown parent"
            )
        return record

    def _checkpoint(self):
        if not self.anchor.exists():
            return None
        try:
            return json.loads(self.anchor.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise IntegrityError("Invalid event log head checkpoint") from exc

    def _stat(self):
        stat = self.path.stat() if self.path.exists() else None
        return (stat.st_ino, stat.st_size, stat.st_mtime_ns) if stat else None

    def _read(self) -> tuple[list[Record], str]:
        """Full verification; never trusts the incremental cache."""
        records, previous, ids, heads = [], "", set(), {}
        raw_data = self.path.read_bytes() if self.path.exists() else b""
        for line_number, raw in enumerate(raw_data.splitlines(keepends=True), 1):
            record = self._parse(raw, line_number, previous, ids)
            records.append(record)
            ids.add(record.id)
            heads[record.branch] = record.id
            previous = hashlib.sha256(raw).hexdigest()
        anchor = self._checkpoint()
        if anchor is not None and anchor != {"lines": len(records), "sha256": previous}:
            raise IntegrityError(f"last line ({len(records)}) was modified or truncated")
        if anchor is None and records:
            raise IntegrityError("Event log head checkpoint is missing")
        self._records, self._digest, self._ids, self._heads = records, previous, ids, heads
        self._offset = len(raw_data)
        self._signature = self._stat()
        self._loaded = True
        return records, previous

    def _incremental(self):
        signature = self._stat()
        size = signature[1] if signature else 0
        checkpoint = self._checkpoint()
        expected = {"lines": len(self._records), "sha256": self._digest}
        if not self._loaded or size < self._offset:
            return self._read()
        if size == self._offset:
            if checkpoint == expected and signature == self._signature:
                return self._records, self._digest
            return self._read()
        if self._signature and signature[0] != self._signature[0]:
            return self._read()
        with self.path.open("rb") as stream:
            stream.seek(self._offset)
            addition = stream.read()
        # Stage changes before updating the cache; malformed growth forces full verification.
        added, previous, ids = [], self._digest, set(self._ids)
        try:
            for number, raw in enumerate(addition.splitlines(keepends=True), len(self._records) + 1):
                record = self._parse(raw, number, previous, ids)
                added.append(record)
                ids.add(record.id)
                previous = hashlib.sha256(raw).hexdigest()
            if checkpoint != {"lines": len(self._records) + len(added), "sha256": previous}:
                return self._read()
        except IntegrityError:
            return self._read()
        self._records.extend(added)
        self._ids, self._digest = ids, previous
        self._heads.update({record.branch: record.id for record in added})
        self._offset = size
        self._signature = signature
        return self._records, self._digest

    def read(self) -> list[Record]:
        with self.lock:
            return self._incremental()[0]

    @property
    def heads(self) -> dict[str, str]:
        self.read()
        return dict(self._heads)

    def verify(self) -> dict:
        with self.lock:
            records, digest = self._read()
        return {"ok": True, "records": len(records), "head_sha256": digest}

    def append(
        self,
        kind: str,
        payload: dict,
        *,
        branch: Any = "main",
        session_id: Any = "engine",
        actor: Any = "engine",
        event_id: Any = None,
        step_id: Any = None,
        parent_id: Any = None,
    ) -> Record:
        with self.lock:
            records, digest = self._incremental()
            heads = self._heads
            if branch not in heads and kind not in ("ProjectCreated", "BranchCreated"):
                raise MlcaUserError(f"Unknown branch: {branch}")
            parent = parent_id if kind == "BranchCreated" else heads.get(branch)
            record = Record(
                type=kind,
                payload=payload,
                branch=branch,
                session_id=session_id,
                actor=actor,
                event_id=event_id,
                step_id=step_id,
                parent_id=parent,
                prev_hash=digest,
            )
            raw = (canonical(record.model_dump(mode="json")) + "\n").encode()
            with self.path.open("ab") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            new_digest = hashlib.sha256(raw).hexdigest()
            atomic_json(self.anchor, {"lines": len(records) + 1, "sha256": new_digest})
            self._records.append(record)
            self._ids.add(record.id)
            self._heads[branch] = record.id
            self._offset += len(raw)
            self._digest = new_digest
            self._signature = self._stat()
        for callback in tuple(self.callbacks):
            callback(record)
        return record


def branch_heads(records: list[Record]) -> dict[str, str]:
    heads = {}
    for record in records:
        heads[record.branch] = record.id
    return heads
