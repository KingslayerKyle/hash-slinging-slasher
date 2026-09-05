#!/usr/bin/env python3
"""Emit exact asset-shaped literals and zone entries from T8 EnhancementMod.

This is a separate public BO4 source corpus.  Zone entries are included as
written (including extensions) because they name the loader-facing asset the
mod links; quoted GSC/CSC/Lua literals retain the game spelling.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "borrowed" / "T8-EnhancementMod"
LITERAL = re.compile(r'(?:#)?["\']([A-Za-z0-9_./\\-]{6,180})["\']')
ZONE = re.compile(r'^(?:image|material|xmodel|xanim|sound|sound_alias|scriptparsetree|luafile),\s*([^,\s]+)', re.I)
EXTENSIONS = {".gsc", ".csc", ".lua", ".zone", ".json", ".cfg", ".txt"}


def clean(value: str) -> str | None:
    value = value.strip().lower().replace("\\", "/")
    if ("_" in value or "/" in value) and sum(char.isalpha() for char in value) >= 3:
        return value
    return None


def main() -> None:
    names = set()
    for path in SOURCE.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        names.update(value for raw in LITERAL.findall(text) if (value := clean(raw)))
        if path.suffix.lower() == ".zone":
            for line in text.splitlines():
                match = ZONE.match(line.strip())
                if match and (value := clean(match.group(1))):
                    names.add(value)
    print("\n".join(sorted(names)))


if __name__ == "__main__":
    main()
