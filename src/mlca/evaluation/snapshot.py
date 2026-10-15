"""A bounded, credential-free snapshot at the first mutation of each session."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from mlca import __version__
from mlca.errors import MlcaUserError
from mlca.sandbox.level import detect


def command(args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=3)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def capture(session):
    cpu = platform.processor() or None
    ram = None
    if sys.platform == "linux":
        try:
            cpu = next(
                line.split(":", 1)[1].strip()
                for line in Path("/proc/cpuinfo").read_text().splitlines()
                if line.startswith("model name")
            )
            ram = (
                int(
                    next(
                        line.split()[1]
                        for line in Path("/proc/meminfo").read_text().splitlines()
                        if line.startswith("MemTotal:")
                    )
                )
                * 1024
            )
        except (OSError, StopIteration, ValueError):
            pass
    else:
        try:
            ram = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
        except (ValueError, OSError, AttributeError):
            pass
    checkout = Path(__file__).resolve().parents[3]
    gpu = (
        command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
        if shutil.which("nvidia-smi")
        else None
    )
    try:
        sandbox = detect(session.config.sandbox.allow_level_b)
    except MlcaUserError:
        sandbox = "unavailable (execution refused)"
    return {
        "mlca_version": __version__,
        "rails": {"version": session.rails.version, "sha256": session.rails.sha256},
        "measurement_arm": session.measurement_arm,
        "git_commit": command(["git", "-C", str(checkout), "rev-parse", "HEAD"])
        if (checkout / ".git").exists()
        else None,
        "python": platform.python_version(),
        "os": platform.system(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "cpu": cpu,
        "logical_cores": os.cpu_count(),
        "ram_bytes": ram,
        "gpu": {
            "value": gpu,
            "source": "exact" if gpu else "unavailable",
            "scope": "NVIDIA inventory only; absence does not prove no GPU",
        },
        "uv_version": command(["uv", "--version"]),
        "bubblewrap_version": command(["bwrap", "--version"]),
        "sandbox_level": sandbox,
        "sandbox_verified": False,
        "template": {
            "id": session.workflow.spec.id,
            "version": session.workflow.spec.version,
            "sha256": session.workflow.sha256,
        },
        "environment_lock_sha256": session.state.lock_sha256,
        "mode": session.mode,
        "principal": session.principal,
        "task_card_sha256": getattr(session, "task_card_sha256", None),
        "roles": {
            role: {
                "provider": cfg.provider,
                "provider_kind": session.config.providers[cfg.provider].kind,
                "model": cfg.model,
                "temperature": cfg.temperature,
                "max_output_tokens": cfg.max_output_tokens,
                "base_url_host": urlparse(session.config.providers[cfg.provider].base_url or "").hostname,
            }
            for role, cfg in session.config.roles.items()
        },
        "sources": {
            "logical_cores": "exact" if os.cpu_count() is not None else "unavailable",
            "ram_bytes": "exact" if ram is not None else "unavailable",
        },
    }
