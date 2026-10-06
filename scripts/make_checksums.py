import hashlib
from pathlib import Path


def main():
    directory = Path("dist")
    files = sorted([*directory.glob("*.whl"), *directory.glob("*.tar.gz")])
    if not files:
        raise SystemExit("No distributions to checksum")
    lines = [hashlib.sha256(file.read_bytes()).hexdigest() + "  " + file.name for file in files]
    (directory / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
