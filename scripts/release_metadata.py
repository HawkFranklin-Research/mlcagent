"""Read author-controlled metadata without importing the application or credentials."""

import ast
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = r"(\d+\.\d+\.\d+)(?:(a|b|rc)(0|[1-9]\d*))?"


def npm_version(version: str) -> str:
    """Map supported PEP 440 releases to npm SemVer without changing Python pins."""
    match = re.fullmatch(VERSION_PATTERN, version)
    if not match:
        raise ValueError("Expected a three-part release, optionally followed by a, b or rc and a number")
    base, phase, number = match.groups()
    label = {"a": "alpha", "b": "beta", "rc": "rc"}.get(phase)
    return f"{base}-{label}.{number}" if phase else base


def metadata(root: Path = ROOT) -> tuple[str, str]:
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    name = project["name"]
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        raise ValueError("The distribution name must be an unscoped Python/npm-compatible name")
    tree = ast.parse((root / "src/mlca/__init__.py").read_text(encoding="utf-8"))
    version = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
    )
    npm_version(version)
    return name, version
