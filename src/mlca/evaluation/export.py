"""Curated run copies with source hashes; private inputs and environments never leave."""

import csv
import json
import shutil
from pathlib import Path

from mlca.errors import MlcaUserError
from mlca.llm.usage import export_csv
from mlca.paths import contained, sha256

RUN_PATHS = (
    "scripts",
    "reports",
    "figures",
    "tables",
    ".mlca/log",
    ".mlca/steps",
    ".mlca/llm",
    ".mlca/requests",
    ".mlca/usage.jsonl",
    ".mlca/egress.jsonl",
    "PROJECT_LOG.md",
    "custom_instructions.md",
    "brain_prompt.md",
    "brain_output.jsonl",
    "brain_stderr.txt",
    "brain_client.json",
)


def export(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if contained(destination, source) or contained(source, destination):
        raise MlcaUserError("Export destination must be separate from the source")
    if destination.exists() and any(destination.iterdir()):
        raise MlcaUserError("Choose a fresh empty export destination")
    manifest = json.loads((source / "bench.json").read_text())
    destination.mkdir(parents=True, exist_ok=True)
    rows = []

    def copy(file, relative):
        if file.is_symlink() or any(p.is_symlink() for p in file.parents if p != source.parent):
            raise MlcaUserError("Symlinks are not permitted in run exports")
        if file.name.endswith((".local.md", ".local.yaml")) or ".mlca/private" in str(relative):
            return
        target = destination / relative
        if not contained(file, source) or not contained(target, destination):
            raise MlcaUserError("Run export path escapes its root")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        digest = sha256(file)
        if sha256(target) != digest:
            raise MlcaUserError("Export checksum mismatch")
        rows.append({"path": str(relative), "sha256": digest, "source_sha256": digest})

    for filename in ("bench.json", "bench_summary.json", "bench_summary.md"):
        if (source / filename).is_file():
            copy(source / filename, Path(filename))
    for run in manifest["runs"]:
        name = run["project"]
        project = source / name
        if not contained(project, source):
            raise MlcaUserError("Run project escapes benchmark output")
        if not project.is_dir():
            continue  # Preserve initialization failures in bench.json.
        for relative in RUN_PATHS:
            path = project / relative
            if path.is_symlink():
                raise MlcaUserError("Symlinks are not permitted in run exports")
            files = path.rglob("*") if path.is_dir() else [path]
            for file in files:
                if file.is_symlink():
                    raise MlcaUserError("Symlinks are not permitted in run exports")
                if file.is_file():
                    copy(file, Path(name) / file.relative_to(project))
        target = destination / name
        target.mkdir(exist_ok=True)
        if (project / ".mlca/requests").is_dir():
            export_csv(project, target / "usage.csv")
            rows.append(
                {
                    "path": name + "/usage.csv",
                    "sha256": sha256(target / "usage.csv"),
                    "source_sha256": "derived from request envelopes",
                }
            )
        metrics = project / "reports/generated/metrics.json"
        if metrics.exists():
            copy(metrics, Path(name) / "metrics.json")
    with (destination / "EXPORT_MANIFEST.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, ["path", "sha256", "source_sha256"])
        writer.writeheader()
        writer.writerows(rows)
    return {"files": len(rows), "destination": str(destination), "private_data_exported": False}
