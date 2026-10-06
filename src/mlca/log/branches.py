import re

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import atomic_json

from .schema import Record
from .store import Store, branch_heads


def ancestry(records: list[Record], head: str | None) -> list[Record]:
    index = {r.id: r for r in records}
    path, seen = [], set()
    while head:
        if head in seen or head not in index:
            raise IntegrityError("Invalid branch ancestry")
        seen.add(head)
        record = index[head]
        path.append(record)
        head = record.parent_id
    return list(reversed(path))


class Branches:
    def __init__(self, store: Store) -> None:
        self.store = store
        self.path = store.path.parent / "branches.json"

    def current(self) -> str:
        records = self.store.read()
        current = "main"
        for record in records:
            if record.type.value == "BranchCheckedOut":
                current = record.payload["name"]
        return current

    def list(self) -> dict:
        return {"current": self.current(), "heads": branch_heads(self.store.read())}

    def records(self, name: str | None = None) -> list[Record]:
        records = self.store.read()
        name = name or self.current()
        heads = branch_heads(records)
        if name not in heads:
            raise MlcaUserError(f"Unknown branch: {name}")
        return ancestry(records, heads[name])

    def create(self, name: str, from_id: str, session_id: str) -> None:
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", name):
            raise MlcaUserError("Branch names must be letters, digits, hyphens or underscores")
        records = self.store.read()
        if name in branch_heads(records):
            raise MlcaUserError("Branch already exists")
        source = next(
            (
                r
                for r in records
                if r.id == from_id or (r.step_id == from_id and r.type.value == "StepCompleted")
            ),
            None,
        )
        if source is None:
            raise MlcaUserError("Unknown branch starting record or completed step")
        self.store.append(
            "BranchCreated",
            {"name": name, "from_record_id": source.id},
            branch=name,
            parent_id=source.id,
            session_id=session_id,
            actor="user",
        )
        self.checkout(name, session_id)

    def checkout(self, name: str, session_id: str) -> None:
        if name not in branch_heads(self.store.read()):
            raise MlcaUserError("Unknown branch")
        self.store.append(
            "BranchCheckedOut", {"name": name}, branch=name, session_id=session_id, actor="user"
        )
        atomic_json(self.path, self.list())
