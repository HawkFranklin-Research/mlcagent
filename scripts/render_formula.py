import argparse
import hashlib
import os
import re
from pathlib import Path

from release_metadata import ROOT, metadata


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha256")
    parser.add_argument("--from-dist", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "packaging/homebrew/mlca.rb")
    args = parser.parse_args()
    name, version = metadata()
    assert (ROOT / "packaging/NAME").read_text(encoding="utf-8").strip() == name, "Run sync_versions.py first"
    digest = args.sha256
    if args.from_dist:
        files = list(args.from_dist.glob("*.tar.gz"))
        if len(files) != 1:
            parser.error("Expected exactly one release sdist")
        digest = hashlib.sha256(files[0].read_bytes()).hexdigest()
    if not digest or not re.fullmatch("[0-9a-f]{64}", digest):
        parser.error("Provide a SHA256 hex digest or --from-dist")
    repository = os.environ.get("PUBLIC_REPOSITORY")
    if repository and not re.fullmatch("[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        parser.error("PUBLIC_REPOSITORY must be owner/repo")
    values = {
        "NAME": name,
        "VERSION": version,
        "SHA256": digest,
        "INITIAL": name[0],
        "HOMEPAGE": "https://github.com/" + repository if repository else f"https://pypi.org/project/{name}/",
    }
    text = (ROOT / "packaging/homebrew/mlca.rb.tmpl").read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("@" + key + "@", value)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
