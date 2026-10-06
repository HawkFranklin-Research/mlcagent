"""Build distributions and verify runtime resources in the wheel (no publication)."""

import argparse
import subprocess
import zipfile
from pathlib import Path

from release_metadata import ROOT


def check(wheel: Path, verbose: bool = True) -> list[str]:
    with zipfile.ZipFile(wheel) as archive:
        files = archive.namelist()
    required = {
        "mlca/__init__.py",
        "mlca/cli/main.py",
        "mlca_runtime/__init__.py",
        "mlca/resources/packaging/NAME",
        "mlca/resources/styles/default.mplstyle",
        "mlca/resources/assets/logo.txt",
        "mlca/resources/assets/logo.png",
        "mlca/resources/assets/banner.txt",
    }
    for template in ("tabular_classification", "survival"):
        required.add(f"mlca/resources/templates/{template}/template.yaml")
        for source in (ROOT / "templates" / template).rglob("*.yaml"):
            required.add("mlca/resources/" + source.relative_to(ROOT).as_posix())
    missing = required - set(files)
    if missing or any("logo_source.png" in path for path in files):
        raise ValueError(
            f"Wheel resources invalid: missing {sorted(missing)}; source artwork must be excluded"
        )
    if verbose:
        print("\n".join(files))
        print(f"PASS: {wheel.name}, {len(files)} entries; all required resources present")
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()
    if args.wheel:
        check(args.wheel)
    else:
        subprocess.run(["uv", "build"], cwd=ROOT, check=True)
        for wheel in sorted((ROOT / "dist").glob("*.whl")):
            check(wheel)


if __name__ == "__main__":
    main()
