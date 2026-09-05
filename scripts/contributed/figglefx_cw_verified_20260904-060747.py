#!/usr/bin/env python3
"""Emit exact verified names from FiggleFX's Cold War hash exports."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "borrowed" / "FiggleFX" / "hashes_cw" / "cw_fx.csv",
    ROOT / "borrowed" / "FiggleFX" / "hashes_cw" / "t9modmanager.csv",
)


def clean(value: str) -> str | None:
    value = value.strip().lower().replace("\\", "/")
    if ("_" in value or "/" in value) and len(value) <= 240 and sum(c.isalpha() for c in value) >= 3:
        return value
    return None


def main() -> None:
    names = set()
    for path in FILES:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if "," in line and (value := clean(line.split(",", 1)[1])):
                names.add(value)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
