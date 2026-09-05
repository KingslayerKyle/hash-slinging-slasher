"""Emit FiggleFX's separate verified BO4 beam and FX-name exports."""

from pathlib import Path
import sys


ROOT = Path("borrowed/FiggleFX/hashes")
SOURCES = (ROOT / "beams_recovered.csv", ROOT / "fx_names.csv")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    seen: set[str] = set()
    for source in SOURCES:
        for raw in source.read_text(encoding="utf-8", errors="replace").splitlines():
            _hash, separator, name = raw.partition(",")
            name = name.strip()
            if separator and name and name not in seen:
                seen.add(name)
                print(name)


if __name__ == "__main__":
    main()
