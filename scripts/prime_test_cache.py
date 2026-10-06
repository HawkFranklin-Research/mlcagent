"""Prime uv's external cache before offline integration tests; never calls model providers."""

import os
import tempfile
from pathlib import Path

from mlca.project.env import create
from mlca.templates.registry import get


def main():
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "mlca-test-setup"
    cache.mkdir(parents=True, exist_ok=True)
    for name in ("tabular_classification", "survival"):
        with tempfile.TemporaryDirectory(prefix=name + "-", dir=cache) as folder:
            record = create(Path(folder), get(name).spec.default_runtime_packages)
            print(f"{name}: {len(record['packages'])} cached analysis packages")


if __name__ == "__main__":
    main()
