#!/usr/bin/env python3
"""Emit exact asset-shaped spellings from the independent BO4 Practice source."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "borrowed" / "BO4-Practice"
LITERAL = re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\-]{6,180})["\']')
VALID = re.compile(r'^[a-z0-9_./-]{6,180}$')
EXTENSIONS = {".gsc", ".csc", ".lua", ".txt", ".json", ".md"}


def clean(value: str) -> str | None:
    value = value.strip().lower().replace("\\", "/")
    if VALID.fullmatch(value) and ("_" in value or "/" in value) and sum(c.isalpha() for c in value) >= 3:
        return value
    return None


def main() -> None:
    names = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        names.update(value for raw in LITERAL.findall(text) if (value := clean(raw)))
        if path.name == "hashes.txt":
            for line in text.splitlines():
                if "," in line and (value := clean(line.split(",", 1)[1])):
                    names.add(value)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
