import json
import os
import shutil
import subprocess
import sys
import zipfile

import pytest

from mlca import __version__


@pytest.mark.slow
def test_wheel_resources_and_fresh_tool(built_wheel, tmp_path):
    with zipfile.ZipFile(built_wheel) as wheel:
        files = wheel.namelist()
        assert "mlca_runtime/__init__.py" in files
        assert "mlca/resources/assets/logo.png" in files
        assert "mlca/resources/packaging/NAME" in files
        assert not any("logo_source.png" in file for file in files)
    home = tmp_path / "clean-home"
    home.mkdir()
    env = {
        **os.environ,
        "HOME": str(home),
        "USERPROFILE": str(home),
        "UV_TOOL_DIR": str(home / "tools"),
        "UV_TOOL_BIN_DIR": str(home / "bin"),
        "UV_CACHE_DIR": subprocess.check_output(["uv", "cache", "dir"], text=True).strip(),
        "XDG_CONFIG_HOME": str(home / "config"),
        "XDG_DATA_HOME": str(home / "data"),
    }
    result = subprocess.run(
        ["uv", "tool", "install", "--python", sys.executable, str(built_wheel)],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    executable = home / "bin" / ("mlca.exe" if os.name == "nt" else "mlca")
    version = subprocess.check_output([str(executable), "--version"], cwd=home, env=env, text=True).strip()
    assert version == __version__
    doctor = json.loads(
        subprocess.check_output([str(executable), "doctor", "--json"], cwd=home, env=env, text=True)
    )
    assert doctor["python"] and doctor["uv"]
    banner = subprocess.check_output(
        [str(executable), "doctor"], cwd=home, env={**env, "FORCE_COLOR": "1", "COLUMNS": "120"}, text=True
    )
    assert "Machine Learning Copilot Agent" in banner
    subprocess.run(["uv", "tool", "uninstall", "mlca"], env=env, check=True, capture_output=True)
    shutil.rmtree(home)
