import pytest

from mlca.api import Session
from mlca.errors import MlcaUserError
from mlca.project.init import initialise
from mlca.project.restart import archive_incomplete, is_incomplete


def test_failed_environment_leaves_no_private_state_and_can_retry(tmp_path, monkeypatch):
    data = tmp_path / "input.csv"
    data.write_text("x,y\n1,0\n2,1\n")
    project = tmp_path / "project"
    project.mkdir()
    keep = project / "keep.txt"
    keep.write_text("user file")

    def failure(*args):
        raise MlcaUserError("environment failed")

    monkeypatch.setattr("mlca.project.init.create", failure)
    with pytest.raises(MlcaUserError):
        initialise(project, [data], "tabular_classification", {})
    assert not (project / ".mlca").exists()
    assert not list(project.glob(".mlca-init-*"))
    assert keep.read_text() == "user file"
    # A second attempt reaches environment creation rather than overwrite refusal.
    with pytest.raises(MlcaUserError, match="environment failed"):
        initialise(project, [data], "tabular_classification", {})


def test_archive_partial_requires_confirmation_and_preserves_evidence(tmp_path):
    private = tmp_path / ".mlca"
    private.mkdir()
    (private / "failed.txt").write_text("evidence")
    assert is_incomplete(tmp_path)
    with pytest.raises(MlcaUserError):
        archive_incomplete(tmp_path, "")
    archived = archive_incomplete(tmp_path, "ARCHIVE INCOMPLETE SETUP")
    assert (archived / "failed.txt").read_text() == "evidence"
    assert not private.exists()


def test_atomic_project_environment_runs_after_rename(project_factory):
    import subprocess

    from mlca.project.env import python

    root = project_factory()
    result = subprocess.run(
        [str(python(root / ".mlca/env")), "-c", 'import mlca_runtime; print("runtime-ready")'],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "runtime-ready"
    assert not list(root.glob(".mlca-init-*"))
    with Session.open(root) as session:
        session.choose("1")
        assert session.store.verify()["ok"]


def test_failed_new_study_removes_only_its_empty_root(tmp_path, monkeypatch):
    data = tmp_path / "input.csv"
    data.write_text("x,y\n1,0\n2,1\n")
    root = tmp_path / "new-study"

    def failure(*args):
        raise MlcaUserError("environment failed")

    monkeypatch.setattr("mlca.project.init.create", failure)
    with pytest.raises(MlcaUserError, match="environment failed"):
        initialise(root, [data], "tabular_classification", {})
    assert not root.exists()
    assert data.exists()
