import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="session")
def built_wheel():
    result = subprocess.run(
        [sys.executable, "scripts/check_wheel.py"], cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr
    wheels = sorted((ROOT / "dist").glob("*.whl"), key=lambda p: p.stat().st_mtime)
    return wheels[-1]
