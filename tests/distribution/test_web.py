import os
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

import pytest
from typer.testing import CliRunner

from mlca.cli.main import app
from mlca.errors import MlcaUserError


def test_missing_web_extra(monkeypatch):
    monkeypatch.setitem(sys.modules, "textual_serve.server", None)
    result = CliRunner().invoke(app, ["web"])
    assert isinstance(result.exception, MlcaUserError)
    assert "Install the web extra" in str(result.exception)


def test_web_loopback_start_stop(tmp_path):
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    process = subprocess.Popen(
        [sys.executable, "-m", "mlca", "--project", str(tmp_path), "web", "--port", str(port)],
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                pytest.fail(stdout + stderr)
            try:
                with urlopen(f"http://127.0.0.1:{port}", timeout=1) as response:
                    assert response.status == 200
                    assert b"MLCA" in response.read()
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("Web server did not start")
    finally:
        process.terminate()
        stdout, stderr = process.communicate(timeout=10)
    assert f"http://127.0.0.1:{port}" in stdout
