from pathlib import Path
import hashlib
import json
import os
from filelock import FileLock
from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import atomic_json, canonical
from .schema import Record


class Store:
    def __init__(self, root: Path):
        self.root = root
        self.path = root / '.mlca/log/events.jsonl'
        self.anchor = root / '.mlca/log/head.json'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = FileLock(str(self.path) + '.lock')
        self.callbacks = []

    def _read(self) -> tuple[list[Record], str]:
        records, previous, ids = [], '', set()
        if self.path.exists():
            for line_number, raw in enumerate(self.path.read_bytes().splitlines(keepends=True), 1):
                try:
                    if not raw.endswith(b'\n'):
                        raise ValueError('Incomplete append')
                    record = Record.model_validate_json(raw)
                    if record.prev_hash != previous or record.id in ids:
                        raise ValueError('Hash chain or duplicate id')
                    if record.parent_id is not None and record.parent_id not in ids:
                        raise ValueError('Unknown parent')
                    records.append(record)
                    ids.add(record.id)
                    previous = hashlib.sha256(raw).hexdigest()
                except Exception as exc:
                    raise IntegrityError(f'Event log integrity failure at line {line_number}') from exc
        if self.anchor.exists():
            anchor = json.loads(self.anchor.read_text())
            if anchor != {'lines': len(records), 'sha256': previous}:
                raise IntegrityError('Event log differs from head checkpoint (edit, truncation or interrupted append)')
        elif records:
            raise IntegrityError('Event log head checkpoint is missing')
        return records, previous

    def read(self) -> list[Record]:
        with self.lock:
            return self._read()[0]

    def verify(self) -> dict:
        with self.lock:
            records, digest = self._read()
        return {'ok': True, 'records': len(records), 'head_sha256': digest}

    def append(self, kind: str, payload: dict, *, branch='main', session_id='engine',
               actor='engine', event_id=None, step_id=None, parent_id=None) -> Record:
        with self.lock:
            records, digest = self._read()
            heads = branch_heads(records)
            if branch not in heads and kind not in ('ProjectCreated', 'BranchCreated'):
                raise MlcaUserError(f'Unknown branch: {branch}')
            parent = parent_id if kind == 'BranchCreated' else heads.get(branch)
            record = Record(type=kind, payload=payload, branch=branch, session_id=session_id,
                            actor=actor, event_id=event_id, step_id=step_id, parent_id=parent,
                            prev_hash=digest)
            raw = (canonical(record.model_dump(mode='json')) + '\n').encode()
            with self.path.open('ab') as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            atomic_json(self.anchor, {'lines': len(records) + 1, 'sha256': hashlib.sha256(raw).hexdigest()})
        for callback in tuple(self.callbacks):
            callback(record)
        return record


def branch_heads(records: list[Record]) -> dict[str, str]:
    heads = {}
    for record in records:
        heads[record.branch] = record.id
    return heads
