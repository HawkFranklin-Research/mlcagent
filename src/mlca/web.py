"""Serve the existing Textual interface on loopback only."""

import shlex
import subprocess
import sys
from pathlib import Path

from mlca.distribution import name
from mlca.errors import MlcaUserError


def serve(project: Path, port: int = 8000) -> None:
    try:
        from textual_serve.server import Server
    except ImportError as exc:
        raise MlcaUserError(
            f'Browser support is missing. Install the web extra: uv tool install "{name()}[web]" --reinstall'
        ) from exc
    args = [sys.executable, "-m", "mlca", "--project", str(project.resolve())]
    command = subprocess.list2cmdline(args) if sys.platform == "win32" else shlex.join(args)
    print(f"MLCA browser interface: http://127.0.0.1:{port}", flush=True)
    Server(command, host="127.0.0.1", port=port, title="MLCA").serve()
