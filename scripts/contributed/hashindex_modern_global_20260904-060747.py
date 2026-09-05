#!/usr/bin/env python3
"""Emit exact labels from HashIndex's unmined modern global exports.

This deliberately excludes BO4 and Cold War, whose HashIndex global/script slice was
confirmed on 2026-09-04, and keeps global labels separate from the script, Lua, and
xasset corpora so each source family remains independently reproducible.
"""
from pathlib import Path


ROOT = Path.cwd()
FILES = (
    "hashes/global/bo6.csv",
    "hashes/global/bo7.csv",
    "hashes/global/mwiii.csv",
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
