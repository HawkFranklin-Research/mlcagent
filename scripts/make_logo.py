"""Regenerate the terminal and desktop logo assets from the source logo image.

    uv run --with pillow --with numpy python scripts/make_logo.py assets/logo_source.png

Writes assets/logo.txt (Braille line art of the figure, without the wordmark) and
assets/logo.png (grayscale 512x512 for desktop and documentation use). Development-only:
pillow and numpy are not runtime dependencies of MLCA.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = 36  # terminal cells; each cell holds 2x4 Braille dots
SUPERSAMPLE = 4  # source pixels per dot side, pooled to keep thin network lines
CONTRAST = 22  # local brightness above the blurred background that counts as ink
BRIGHT = 175  # absolute brightness that always counts as ink (head, nodes)
COVERAGE = 0.35  # share of ink pixels needed to set a dot
FIGURE_BOX = (0.05, 0.08, 0.95, 0.62)  # crop of the source: figure only, no lettering
DOTS = [
    (0, 0, 0x01),
    (1, 0, 0x02),
    (2, 0, 0x04),
    (0, 1, 0x08),
    (1, 1, 0x10),
    (2, 1, 0x20),
    (3, 0, 0x40),
    (3, 1, 0x80),
]


def braille(image: Image.Image) -> list[str]:
    w, h = image.size
    box = (int(w * FIGURE_BOX[0]), int(h * FIGURE_BOX[1]), int(w * FIGURE_BOX[2]), int(h * FIGURE_BOX[3]))
    figure = image.convert("RGB").crop(box)
    k, width = SUPERSAMPLE, COLUMNS * 2
    height = max(4, round(figure.size[1] / figure.size[0] * width / 4) * 4)  # Braille dots are square
    gray = figure.resize((width * k, height * k), Image.LANCZOS).convert("L")
    lum = np.asarray(gray, dtype=float)
    background = np.asarray(gray.filter(ImageFilter.GaussianBlur(k * 2)), dtype=float)
    ink = ((lum - background) > CONTRAST) | (lum > BRIGHT)
    dots = ink.reshape(height, k, width, k).mean(axis=(1, 3)) > COVERAGE
    lines = []
    for row in range(0, height, 4):
        cells = []
        for col in range(0, width, 2):
            code = sum(bit for dy, dx, bit in DOTS if dots[row + dy, col + dx])
            cells.append(chr(0x2800 + code) if code else " ")
        lines.append("".join(cells).rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def main() -> None:
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets/logo_source.png"
    image = Image.open(source)
    (ROOT / "assets/logo.txt").write_text("\n".join(braille(image)) + "\n")
    gray = ImageOps.autocontrast(ImageOps.grayscale(image.convert("RGB")))
    side = max(gray.size)
    square = Image.new("L", (side, side), 0)
    square.paste(gray, ((side - gray.size[0]) // 2, (side - gray.size[1]) // 2))
    square.resize((512, 512), Image.LANCZOS).save(ROOT / "assets/logo.png", optimize=True)


if __name__ == "__main__":
    main()
