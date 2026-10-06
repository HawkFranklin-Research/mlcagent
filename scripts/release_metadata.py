"""Read author-controlled metadata without importing the application or credentials."""

import ast
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def metadata(root: Path = ROOT) -> tuple[str, str]:
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    name = project["name"]
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
        raise ValueError("The distribution name must be an unscoped Python/npm-compatible name")
    tree = ast.parse((root / "src/mlca/__init__.py").read_text())
    version = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__version__" for target in node.targets)
    )
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise ValueError("Release wrappers currently require a stable three-part version")
    return name, version
