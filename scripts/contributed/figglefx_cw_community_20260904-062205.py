#!/usr/bin/env python3
"""Emit exact names from FiggleFX's separate Cold War community hash export."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "borrowed" / "FiggleFX" / "hashes_cw" / "community.csv"


def clean(value: str) -> str | None:
    value = value.strip().lower().replace("\\", "/")
    if ("_" in value or "/" in value) and len(value) <= 240 and sum(c.isalpha() for c in value) >= 3:
        return value
    return None


def main() -> None:
    names = set()
    for line in SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "," in line and (value := clean(line.split(",", 1)[1])):
            names.add(value)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
