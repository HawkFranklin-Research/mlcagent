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
