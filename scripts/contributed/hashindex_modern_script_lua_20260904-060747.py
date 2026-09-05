#!/usr/bin/env python3
"""Emit HashIndex's unmined modern script and Lua labels, separately from globals."""
from pathlib import Path


ROOT = Path.cwd()
FILES = (
    "hashes/scr/bo6.csv",
    "hashes/scr/mwiii.csv",
    "hashes/lua/bo6.csv",
)


def main() -> None:
    index = ROOT / "borrowed" / "HashIndex"
    labels: set[str] = set()
    for relative in FILES:
        with (index / relative).open(encoding="utf-8", errors="ignore") as source:
            for line in source:
                _, separator, label = line.rstrip("\n\r").partition(",")
                label = label.strip()
                if separator and label:
                    labels.add(label)
    for label in sorted(labels):
        print(label)


if __name__ == "__main__":
    main()
