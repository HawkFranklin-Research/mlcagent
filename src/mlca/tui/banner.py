"""Compact MLCA banner: Braille logo, two-row wordmark and a few status lines.

Shared by the Textual welcome screen and the command-line client. Narrow terminals get the
wordmark only. Regenerate the logo art with scripts/make_logo.py.
"""

from pathlib import Path
from typing import Any

from rich.console import Console, Group
from rich.table import Table
from rich.text import Text

from mlca import __version__
from mlca.paths import resource
from mlca.ui_text import text

WORDMARK = ("█▀▄▀█ █   █▀▀ ▄▀█", "█ ▀ █ █▄▄ █▄▄ █▀█")
HEAD = "#f2f5f8"  # light grey-white: the figure's head and suit
NETWORK = "#5fb4f0"  # blue: the neural networks on either side
MUTED = "#8a96a3"
HEAD_BAND = (0.37, 0.64)  # horizontal share of the logo occupied by the head
MIN_WIDTH = 84  # below this, show the wordmark only


def logo_lines() -> list[str]:
    path = resource("assets") / "logo.txt"
    return path.read_text().splitlines() if path.exists() else []


def logo() -> Text:
    lines = logo_lines()
    width = max((len(line) for line in lines), default=0)
    art = Text(no_wrap=True)
    for n, line in enumerate(lines):
        for col, char in enumerate(line):
            inside = HEAD_BAND[0] <= col / max(width, 1) <= HEAD_BAND[1]
            art.append(char, style=HEAD if inside or n == len(lines) - 1 else NETWORK)
        if n < len(lines) - 1:
            art.append("\n")
    return art


def short_path(path: Path | None, limit: int = 48) -> str:
    """Home-relative path, shortened to its last parts when it is long."""
    if path is None:
        return ""
    path = Path(path).expanduser().resolve()
    try:
        shown = "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        shown = str(path)
    if len(shown) > limit:
        shown = "…/" + "/".join(path.parts[-2:])
    return shown


def _details(project: Path | None, extra: list[str] | None) -> Text:
    info = Text(no_wrap=True)
    info.append(WORDMARK[0] + "\n", style=f"bold {HEAD}")
    info.append(WORDMARK[1] + "\n", style=f"bold {HEAD}")
    info.append(text("tagline") + "\n", style=NETWORK)
    info.append(f"v{__version__} · {text('subtitle')}", style=MUTED)
    lines = ([short_path(project)] if project else []) + (extra or [])
    for line in lines:
        info.append("\n" + line, style=MUTED)
    return info


def banner(width: int = 100, project: Path | None = None, extra: list[str] | None = None) -> Any:
    details = _details(project, extra)
    if width < MIN_WIDTH or not logo_lines():
        return details
    grid = Table.grid(padding=(0, 3))
    grid.add_column(no_wrap=True)
    grid.add_column(no_wrap=True, vertical="middle")
    grid.add_row(logo(), details)
    return Group(grid)


def print_banner(project: Path | None = None, extra: list[str] | None = None) -> None:
    """Print the banner on an interactive terminal; stay silent when output is piped."""
    console = Console()
    if console.is_terminal:
        console.print(banner(console.width, project, extra))
        console.print()


def brand_line(project: Path | None = None) -> Text:
    """One-line brand for the top of the main screen."""
    line = Text(no_wrap=True, overflow="ellipsis")
    line.append(" ▌", style=NETWORK)
    line.append("MLCA ", style=f"bold {HEAD}")
    line.append(text("tagline"), style=NETWORK)
    line.append(f"  v{__version__}", style=MUTED)
    if project:
        line.append(f"  ·  {short_path(project)}", style=MUTED)
    return line
