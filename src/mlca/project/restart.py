"""Allocate a fresh study without replacing an earlier attempt's evidence."""

from pathlib import Path

from mlca.errors import MlcaUserError


def reserve_fresh_study(parent: Path) -> Path:
    parent = parent.expanduser().resolve()
    if not parent.is_dir():
        raise MlcaUserError("Choose an existing project folder before creating a fresh study")
    for number in range(1, 10001):
        path = parent / f"study-{number:03d}"
        try:
            path.mkdir()
        except FileExistsError:
            continue
        return path
    raise MlcaUserError("No free study subfolder name; choose another project folder")


def is_incomplete(path: Path) -> bool:
    import json

    private = path / ".mlca"
    if not private.is_dir() or private.is_symlink():
        return False
    records = private / "log/events.jsonl"
    if not records.exists():
        return True
    try:
        return not any(
            json.loads(line).get("type") == "EventEntered" for line in records.read_text().splitlines()
        )
    except (OSError, ValueError):
        return False  # Corrupt history is not classified as a disposable partial initialization.


def archive_incomplete(path: Path, confirmation: str) -> Path:
    import hashlib
    import os
    import uuid

    from filelock import FileLock

    from mlca.paths import user_data_dir

    path = path.expanduser().resolve()
    if confirmation != "ARCHIVE INCOMPLETE SETUP":
        raise MlcaUserError("Type ARCHIVE INCOMPLETE SETUP to archive the old private state")
    locks = user_data_dir() / "init-locks"
    locks.mkdir(parents=True, exist_ok=True)
    with FileLock(str(locks / (hashlib.sha256(str(path).encode()).hexdigest() + ".lock"))):
        if not is_incomplete(path):
            raise MlcaUserError("This is not an incomplete setup; open it or create a fresh study")
        destination = path / (".mlca-incomplete-" + uuid.uuid4().hex)
        os.rename(path / ".mlca", destination)
        return destination
