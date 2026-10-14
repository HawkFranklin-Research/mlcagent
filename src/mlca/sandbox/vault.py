import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from cryptography.fernet import Fernet

from mlca.errors import IntegrityError, MlcaUserError
from mlca.paths import sha256, user_data_dir


def seal(project_id: str, split_id: str, data: bytes, destination: Path) -> None:
    directory = user_data_dir() / "keys"
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    key_path = directory / f"{project_id}_{split_id}.key"
    key = Fernet.generate_key()
    fd = os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(key)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(Fernet(key).encrypt(data))
    destination.chmod(0o600)


@contextmanager
def exposed(root: Path, state: Any, step_id: str, emit: Any) -> Any:
    if not state.split or not state.test_unlocked:
        raise MlcaUserError("Test partition is locked")
    split = state.split
    vault = root / split["vault"]["path"]
    if sha256(vault) != split["vault"]["sha256"]:
        raise IntegrityError("Encrypted test partition changed")
    key_path = user_data_dir() / "keys" / f"{state.project_id}_{split['split_id']}.key"
    key = key_path.read_bytes()
    data = Fernet(key).decrypt(vault.read_bytes())
    folder = root / ".mlca/data/exposed"
    folder.mkdir(exist_ok=True)
    fd, name = tempfile.mkstemp(dir=folder, suffix=".parquet")
    path = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
        path.chmod(0o400)
        emit("TestRead", {"step_id": step_id, "split_sha256": split["sha256"]})
        yield path
    finally:
        path.chmod(0o600)
        path.unlink(missing_ok=True)


@contextmanager
def exposed_external(session, step_id):
    """One exposure per frozen model variant, across branches and failed attempts."""
    import hashlib
    from contextlib import ExitStack

    state = session.state
    if not state.test_unlocked or state.current_event not in {"test", "interpret"}:
        raise MlcaUserError("External cohort is locked", category="test_lock")
    models = sorted(
        o["sha256"]
        for s in state.steps
        if s["event_id"] == "model" and s["status"] == "completed"
        for o in s.get("outputs", [])
        if o["kind"] == "model"
    )
    variant = hashlib.sha256("|".join(models).encode()).hexdigest()
    used = {
        (r.payload["name"], r.payload["variant"])
        for r in session.store.read()
        if r.type.value == "ExternalRead"
    }
    if any((name, variant) in used for name in state.external):
        raise MlcaUserError(
            "External cohort already exposed for this frozen model variant", category="test_lock"
        )
    paths = {}
    with ExitStack() as stack:
        for name, item in state.external.items():
            vault = session.root / item["path"]
            if sha256(vault) != item["sha256"]:
                raise IntegrityError("Encrypted external cohort changed")
            key = (user_data_dir() / "keys" / f"{state.project_id}_{item['key_id']}.key").read_bytes()
            data = Fernet(key).decrypt(vault.read_bytes())
            if __import__("hashlib").sha256(data).hexdigest() != item["plain_sha256"]:
                raise IntegrityError("External cohort plaintext hash differs")
            folder = session.root / ".mlca/data/exposed"
            folder.mkdir(parents=True, exist_ok=True)
            fd, filename = tempfile.mkstemp(dir=folder, suffix=".parquet")
            path = Path(filename)
            stack.callback(path.unlink, missing_ok=True)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
            path.chmod(0o400)
            session.emit("ExternalRead", {"name": name, "variant": variant, "step_id": step_id})
            paths["external" if len(state.external) == 1 else "external_" + name] = path
        yield paths
