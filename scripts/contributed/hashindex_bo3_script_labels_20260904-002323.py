#!/usr/bin/env python3
"""Emit BO3 script labels from HashIndex for cross-era BO4/CW confirmation."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'borrowed' / 'HashIndex' / 'hashes' / 'scr' / 'bo3.csv'


if __name__ == '__main__':
    names = set()
    for line in SOURCE.read_text(encoding='utf-8', errors='ignore').splitlines():
        _, separator, name = line.partition(',')
        name = name.strip()
        if separator and name:
            names.add(name)
    print('\n'.join(sorted(names)))
