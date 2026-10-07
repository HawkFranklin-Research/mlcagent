import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from mlca import __version__

ROOT = Path(__file__).resolve().parents[2]


def test_synced_wrapper_metadata():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/sync_versions.py"), "--check"], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    package = json.loads((ROOT / "packaging/npm/package.json").read_text())
    assert not package.get("scripts")
    assert package["engines"]["node"] == ">=18"


@pytest.mark.skipif(os.name == "nt", reason="POSIX installer; Windows installer is parsed separately")
@pytest.mark.parametrize(
    "installed, version, no_modify", [(False, None, False), (True, None, True), (False, "0.2.0", True)]
)
def test_shell_installer_dry_run(tmp_path, installed, version, no_modify):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    record = tmp_path / "commands.txt"
    uv = bin_dir / "uv"
    uv.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$*" >> "$FAKE_COMMANDS"\ncase "$*" in\n "tool list") [ "$FAKE_INSTALLED" = yes ] && echo "mlca v0.1.0"; exit 0 ;;\n "tool dir --bin") echo "$FAKE_BIN" ;;\nesac\n'
    )
    uv.chmod(0o755)
    mlca = bin_dir / "mlca"
    mlca.write_text('#!/bin/sh\nprintf "mlca %s\\n" "$*" >> "$FAKE_COMMANDS"\n')
    mlca.chmod(0o755)
    env = {
        **os.environ,
        "HOME": str(tmp_path),
        "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"],
        "FAKE_COMMANDS": str(record),
        "FAKE_INSTALLED": "yes" if installed else "no",
        "FAKE_BIN": str(bin_dir),
    }
    args = ["sh", str(ROOT / "installers/install.sh"), "--yes"]
    if version:
        args += ["--version", version]
    if no_modify:
        args += ["--no-modify-path"]
    result = subprocess.run(args, env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    calls = record.read_text()
    default_version = __version__ if any(c.isalpha() for c in __version__) else None
    pin = version or default_version
    expected = (
        "tool install --reinstall mlca==" + pin
        if pin
        else "tool upgrade mlca"
        if installed
        else "tool install mlca"
    )
    assert expected in calls
    assert ("tool update-shell" in calls) == (not no_modify)
    assert "mlca doctor" in calls
    assert "sudo " not in calls
    subprocess.run(["sh", "-n", str(ROOT / "installers/install.sh")], check=True)
    if shutil.which("shellcheck"):
        subprocess.run(["shellcheck", str(ROOT / "installers/install.sh")], check=True)


def test_powershell_syntax_when_available():
    if not shutil.which("pwsh"):
        pytest.skip("pwsh and PSScriptAnalyzer are unavailable on this host")
    script = str(ROOT / "installers/install.ps1").replace("'", "''")
    code = f"$errors=$null; $tokens=$null; [System.Management.Automation.Language.Parser]::ParseFile('{script}', [ref]$tokens, [ref]$errors) | Out-Null; if ($errors.Count) {{ $errors | Out-String | Write-Error; exit 1 }}; if (Get-Module -ListAvailable PSScriptAnalyzer) {{ $issues=Invoke-ScriptAnalyzer -Path '{script}' -Severity Error; if ($issues) {{ $issues | Out-String | Write-Error; exit 1 }} }}"
    subprocess.run(["pwsh", "-NoProfile", "-Command", code], check=True)


def test_node_launcher_and_pack(tmp_path):
    if not shutil.which("node") or not shutil.which("npm"):
        pytest.skip("Node/npm unavailable")
    env = {**os.environ, "MLCA_TEST_PYTHON": sys.executable, "MLCA_TEST_UV": shutil.which("uv")}
    result = subprocess.run(
        ["node", "--test", "packaging/npm/test/"], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    npm = shutil.which("npm")
    # npm is a .cmd entry point on Windows; subprocess needs the command interpreter there.
    args = [npm, "pack", "--dry-run", "--json"]
    if os.name == "nt":
        args = ["cmd", "/d", "/s", "/c", subprocess.list2cmdline(args)]
    result = subprocess.run(args, cwd=ROOT / "packaging/npm", env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    raw = json.loads(result.stdout)
    package = raw[0] if isinstance(raw, list) else raw if "files" in raw else next(iter(raw.values()))
    files = {item["path"] for item in package["files"]}
    assert files == {"package.json", "bin/mlca.js", "README.md", "LICENSE"}


def test_render_homebrew(tmp_path):
    formula = tmp_path / "mlca.rb"
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/render_formula.py"),
            "--sha256",
            "0" * 64,
            "--output",
            str(formula),
        ],
        check=True,
        capture_output=True,
    )
    content = formula.read_text()
    assert 'depends_on "uv"' in content and 'tool run --from "mlca==' in content
    if shutil.which("ruby"):
        subprocess.run(["ruby", "-c", str(formula)], check=True, capture_output=True)
