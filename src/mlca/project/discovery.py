"""Discover supported tables without merging them or following directory symlinks."""

from pathlib import Path

from mlca.errors import MlcaUserError

SUPPORTED = {".csv", ".tsv", ".parquet", ".pq"}
EXCLUDED = {".git", ".mlca", ".venv", "__pycache__", ".ipynb_checkpoints"}


def discover(paths: list[Path]) -> list[Path]:
    found = []
    for value in paths:
        path = value.expanduser()
        if path.is_symlink():
            raise MlcaUserError(f"Select the original file/folder rather than a symlink: {path}")
        if path.is_dir():
            candidates = sorted(path.rglob("*"))
            for candidate in candidates:
                relative = candidate.relative_to(path)
                if any(part.startswith(".") or part in EXCLUDED for part in relative.parts):
                    continue
                if candidate.is_symlink() or any(p.is_symlink() for p in candidate.parents if p != path):
                    continue
                if candidate.is_file() and candidate.suffix.lower() in SUPPORTED:
                    found.append(candidate.resolve())
        elif path.is_file() and path.suffix.lower() in SUPPORTED:
            found.append(path.resolve())
        else:
            raise MlcaUserError(f"Select a folder or supported table (CSV, TSV, Parquet): {path}")
    found = list(dict.fromkeys(found))
    if not found:
        raise MlcaUserError("No supported tables found; choose CSV, TSV or Parquet data")
    return found


def registrations(paths: list[Path]) -> list[tuple[str, Path]]:
    """Stable unique references even when different folders contain equal file stems."""
    result = []
    used = set()
    for path in paths:
        name = path.stem
        number = 2
        while name in used:
            name = f"{path.stem}_{number}"
            number += 1
        used.add(name)
        result.append((name, path))
    return result
