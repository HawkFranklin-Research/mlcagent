"""Refuse release preparation until licence/name decisions and the version tag are approved."""

import argparse
from pathlib import Path

from release_metadata import ROOT, metadata


def verify(root: Path, tag: str, approved_name: str) -> tuple[str, str]:
    name, version = metadata(root)
    license_text = (root / "LICENSE").read_text().strip()
    if not license_text or any(
        marker in license_text.lower()
        for marker in ("placeholder", "license to be chosen", "no license is granted")
    ):
        raise ValueError("D1 unresolved: replace the LICENSE placeholder with the author-chosen licence")
    if approved_name != name:
        raise ValueError("D3 unresolved: PACKAGE_NAME_APPROVED must match project.name in pyproject.toml")
    if tag != "v" + version:
        raise ValueError(f"Release tag must be v{version}, received {tag!r}")
    if (root / "packaging/NAME").read_text().strip() != name:
        raise ValueError("Generated packaging/NAME is stale; run scripts/sync_versions.py")
    return name, version


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--approved-name", required=True)
    args = parser.parse_args()
    try:
        name, version = verify(args.root, args.tag, args.approved_name)
    except ValueError as exc:
        parser.exit(1, str(exc) + "\n")
    print(f"Release metadata verified: {name} {version}")


if __name__ == "__main__":
    main()
