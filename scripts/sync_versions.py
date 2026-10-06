"""Generate all wrapper identities from pyproject.toml and __version__; never publishes."""

import argparse
import json

from release_metadata import ROOT, metadata


def sync(check: bool = False):
    name, version = metadata()
    updates = {ROOT / "packaging/NAME": name + "\n"}
    # Consumers read the generated mirror after syncing it from the sole authority.
    chosen = name if not check else (ROOT / "packaging/NAME").read_text().strip()
    package = {
        "name": chosen,
        "version": version,
        "description": "Launcher for the MLCA Python workflow harness",
        "bin": {"mlca": "bin/mlca.js"},
        "engines": {"node": ">=18"},
        "files": ["bin/mlca.js", "README.md", "LICENSE"],
        "license": "SEE LICENSE IN LICENSE",
        "mlca": {"pythonName": chosen},
        "publishConfig": {"access": "public"},
    }
    updates[ROOT / "packaging/npm/package.json"] = json.dumps(package, indent=2) + "\n"
    updates[ROOT / "packaging/npm/LICENSE"] = (ROOT / "LICENSE").read_text()
    for kind in ("sh", "ps1"):
        updates[ROOT / f"installers/install.{kind}"] = (
            (ROOT / f"installers/install.{kind}.tmpl").read_text().replace("@NAME@", chosen)
        )
    mismatches = [
        str(path.relative_to(ROOT))
        for path, value in updates.items()
        if not path.exists() or path.read_text() != value
    ]
    if check and mismatches:
        raise SystemExit("Generated wrapper metadata is stale: " + ", ".join(mismatches))
    if not check:
        for path, value in updates.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value)
        (ROOT / "installers/install.sh").chmod(0o755)
        (ROOT / "packaging/npm/bin/mlca.js").chmod(0o755)
    print(f"{name} {version}: wrapper metadata " + ("checked" if check else "synced"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    sync(parser.parse_args().check)
