import hashlib
import json
import os
import tempfile
from importlib.resources import files
from pathlib import Path


def user_config_dir() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "mlca"


def user_data_dir() -> Path:
    return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "mlca"


def resource(name: str) -> Path:
    local = Path(__file__).resolve().parents[2] / name
    if local.is_dir():
        return local
    return Path(str(files("mlca").joinpath("resources", name)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix="." + path.name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(canonical(value) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def contained(path: Path, root: Path) -> bool:
    return path.resolve().is_relative_to(root.resolve())


def directory_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(path.rglob("*.py")):
        if "__pycache__" not in file.parts:
            digest.update(str(file.relative_to(path)).encode())
            digest.update(file.read_bytes())
    return digest.hexdigest()
