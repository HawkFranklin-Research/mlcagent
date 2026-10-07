import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_release_decision_guards(tmp_path):
    (tmp_path / "src/mlca").mkdir(parents=True)
    (tmp_path / "packaging").mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nname="example-name"\n')
    (tmp_path / "src/mlca/__init__.py").write_text('__version__ = "1.2.3"\n')
    (tmp_path / "packaging/NAME").write_text("example-name\n")

    def invoke(tag="v1.2.3", approved="example-name"):
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/verify_release.py"),
                "--root",
                str(tmp_path),
                "--tag",
                tag,
                "--approved-name",
                approved,
            ],
            capture_output=True,
            text=True,
        )

    (tmp_path / "LICENSE").write_text(
        "License to be chosen by the author. No license is granted by this placeholder."
    )
    assert "D1 unresolved" in invoke().stderr
    (tmp_path / "LICENSE").write_text("MIT License\nCopyright test\nPermission is hereby granted...")
    assert "D3 unresolved" in invoke(approved="").stderr
    assert "Release tag must be" in invoke(tag="v9.9.9").stderr
    assert invoke().returncode == 0


def test_workflows_parse_and_publish_is_protected():
    for name in ("ci.yml", "release.yml"):
        data = yaml.load((ROOT / ".github/workflows" / name).read_text(), Loader=yaml.BaseLoader)
        assert data["on"] and data["jobs"]
    release = yaml.load((ROOT / ".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader)
    for name in ("publish-pypi", "github-release", "publish-npm", "update-homebrew"):
        assert release["jobs"][name]["environment"] == "release"
        assert release["jobs"][name]["needs"]
    assert release["jobs"]["publish-pypi"]["permissions"]["id-token"] == "write"
    assert release["jobs"]["build"]["needs"] == "verify"


@pytest.mark.parametrize(
    "python_version, semver",
    [
        ("0.2.0", "0.2.0"),
        ("0.2.0b1", "0.2.0-beta.1"),
        ("1.2.3a2", "1.2.3-alpha.2"),
        ("1.2.3rc1", "1.2.3-rc.1"),
    ],
)
def test_prerelease_metadata(tmp_path, monkeypatch, python_version, semver):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    from release_metadata import metadata, npm_version
    from verify_release import verify

    (tmp_path / "src/mlca").mkdir(parents=True)
    (tmp_path / "packaging").mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nname="mlca"\n')
    (tmp_path / "src/mlca/__init__.py").write_text(f'__version__ = "{python_version}"\n')
    (tmp_path / "packaging/NAME").write_text("mlca\n")
    (tmp_path / "LICENSE").write_text((ROOT / "LICENSE").read_text())
    assert metadata(tmp_path) == ("mlca", python_version)
    assert npm_version(python_version) == semver
    assert verify(tmp_path, "v" + python_version, "mlca") == ("mlca", python_version)


def test_beta_wrapper_uses_python_pin():
    import json

    from mlca import __version__

    package = json.loads((ROOT / "packaging/npm/package.json").read_text())
    assert package["mlca"]["pythonVersion"] == __version__
    assert package["license"] == "CC-BY-NC-ND-4.0"
    if __version__ == "0.2.0b1":
        assert package["version"] == "0.2.0-beta.1"
        assert "VERSION='0.2.0b1'" in (ROOT / "installers/install.sh").read_text()
        assert "$Version = '0.2.0b1'" in (ROOT / "installers/install.ps1").read_text()
