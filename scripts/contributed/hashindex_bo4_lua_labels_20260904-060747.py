#!/usr/bin/env python3
"""Emit plaintext labels from HashIndex's separate BO4 Lua hash table."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    path = ROOT / 'borrowed' / 'HashIndex' / 'hashes' / 'lua' / 'bo4.csv'
    names = set()
    for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
        _, separator, name = line.partition(',')
        name = name.strip()
        if separator and name:
            names.add(name)
    print('\n'.join(sorted(names)))
