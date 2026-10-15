"""Research-side genericity check: headers only, no held-out file access."""

import csv
import re
from pathlib import Path

import yaml

from mlca.rails import load


def test_rails_are_generic():
    root = Path(__file__).resolve().parents[2]
    manifest = yaml.safe_load((root / "benchmarks/manifest.yaml").read_text())
    entries = manifest if isinstance(manifest, list) else manifest["datasets"]
    forbidden = set()
    for entry in entries:
        if entry["role"] != "development":
            continue
        forbidden.update([entry["id"], Path(entry["file"]).name])
        with (root / "benchmarks" / entry["file"]).open(newline="") as stream:
            forbidden.update(next(csv.reader(stream)))
    for rail in load(root / "rails").items:
        for token in forbidden:
            assert not re.search(
                r"(?<!\w)" + re.escape(token) + r"(?!\w)", rail.text + " " + rail.reason, re.I
            ), token
