from mlca.paths import resource


def name() -> str:
    """Generated from pyproject.toml by scripts/sync_versions.py."""
    return (resource("packaging") / "NAME").read_text().strip()
