import shutil
import sys
from typing import Any

from mlca.errors import MlcaUserError


def detect(allow_level_b: Any = False) -> str:
    if sys.platform == "linux" and shutil.which("bwrap"):
        return "A"
    if allow_level_b:
        return "B"
    raise MlcaUserError(
        "Bubblewrap isolation is unavailable; explicitly opt into level B to run trusted code"
    )


def explanation(platform: str | None = None, bwrap: bool | None = None) -> str:
    platform = platform or sys.platform
    available = (platform == "linux" and bool(shutil.which("bwrap"))) if bwrap is None else bwrap
    opt_in = "Set sandbox.allow_level_b: true in config.yaml to run trusted code with the weaker audit hook."
    if platform == "linux" and available:
        return "Level A uses bubblewrap filesystem/network namespaces; capability is confirmed on execution."
    if platform == "win32":
        return (
            "Native Windows uses level B only with explicit opt-in. For level A, use WSL2 (wsl --install) and install bubblewrap inside WSL. "
            + opt_in
        )
    if platform == "darwin":
        return "macOS uses level B only with explicit opt-in; it is not an OS security boundary. " + opt_in
    return "Level A is unavailable until bubblewrap is installed on Linux. " + opt_in
