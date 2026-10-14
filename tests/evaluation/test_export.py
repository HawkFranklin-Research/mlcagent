import json

import pytest

from mlca.errors import MlcaUserError
from mlca.evaluation.export import export
from mlca.paths import sha256


def test_export_copies_allowlist_and_never_private(tmp_path):
    source, destination = tmp_path / "source", tmp_path / "export"
    source.mkdir()
    (source / "bench.json").write_text(json.dumps({"runs": [{"project": "run-001"}]}))
    project = source / "run-001"
    for name in [
        "scripts/step.py",
        ".mlca/log/events.jsonl",
        ".mlca/steps/one/script.py",
        ".mlca/llm/one.json",
        "reports/generated/metrics.json",
        "custom_instructions.md",
        ".mlca/private/key",
        ".mlca/vault/data.enc",
        ".mlca/env/bin/python",
        ".mlca/data/rows.csv",
        "reports/private.local.md",
    ]:
        file = project / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("fixture")
    result = export(source, destination)
    assert not result["private_data_exported"]
    for name in [
        "scripts/step.py",
        ".mlca/log/events.jsonl",
        ".mlca/steps/one/script.py",
        "custom_instructions.md",
    ]:
        assert sha256(project / name) == sha256(destination / "run-001" / name)
    for name in [".mlca/private", ".mlca/env", ".mlca/vault", ".mlca/data", "reports/private.local.md"]:
        assert not (destination / "run-001" / name).exists()
    assert (destination / "run-001/metrics.json").exists()


def test_export_refuses_symlinks_and_path_escape(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "bench.json").write_text(json.dumps({"runs": [{"project": "../outside"}]}))
    with pytest.raises(MlcaUserError, match="escapes"):
        export(source, tmp_path / "export")
    (source / "bench.json").write_text(json.dumps({"runs": [{"project": "run-001"}]}))
    project = source / "run-001/scripts"
    project.mkdir(parents=True)
    (project / "secret").symlink_to("/etc/passwd")
    with pytest.raises(MlcaUserError, match="Symlinks"):
        export(source, tmp_path / "other")
