#!/usr/bin/env python3
"""Duplicate each basename character of known CW non-sound assets once.

This is the inverse of a one-character deletion, but only varies a spelling already
attested by a real asset.  Earlier CW probes duplicated token edge positions; this
covers every alphanumeric position, including bare basenames and short tokens.
"""
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names(*TABLES)
        if name.strip()
    }
    for kind in ("xmodel", "material", "image", "xanim"):
        known.update(
            name.strip().lower().replace("\\", "/")
            for name in snapshot.confirmed_names(kind)
            if name.strip()
        )

    controls = 0
    emitted = 0
    for name in sorted(known):
        head, slash, base = name.rpartition("/")
        prefix = head + slash if slash else ""
        if not base or len(base) > 96:
            continue
        for position, char in enumerate(base):
            if not char.isascii() or not char.isalnum():
                continue
            candidate = prefix + base[:position] + char + base[position:]
            if candidate in known:
                controls += 1
            else:
                print(candidate)
                emitted += 1
    print(f"positive controls: {controls:,}; candidates: {emitted:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
