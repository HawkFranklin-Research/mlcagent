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
