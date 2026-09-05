#!/usr/bin/env python3
"""Emit exact names from FiggleFX's verified BO4 general hash exports.

The dedicated xmodel/image/material dumps are held aside: this pass is the
independent community, mined, source-name, and WNI-verified corpus only.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "borrowed" / "FiggleFX" / "hashes"
FILES = ("community.csv", "mined.csv", "srcnames.csv", "wni_verified.csv")


def clean(value: str) -> str | None:
    value = value.strip().lower().replace("\\", "/")
    if ("_" in value or "/" in value) and len(value) <= 240 and sum(c.isalpha() for c in value) >= 3:
        return value
    return None


def main() -> None:
    names = set()
    for name in FILES:
        for line in (FOLDER / name).read_text(encoding="utf-8", errors="ignore").splitlines():
            if "," in line and (value := clean(line.split(",", 1)[1])):
                names.add(value)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
