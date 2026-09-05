#!/usr/bin/env python3
"""Emit HashIndex's unmined typed modern xasset labels, not global/script labels."""
from pathlib import Path


ROOT = Path.cwd()
FILES = (
    "hashes/xassets/xassets_bo6.csv",
    "hashes/xassets/ximages_mw5.csv",
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
