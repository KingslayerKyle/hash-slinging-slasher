#!/usr/bin/env python3
"""Fill high-control terminal left/right material counterparts.

The entire basename before the final `_left` or `_right` is held fixed.  The
relation needs 100 complete same-base controls, preventing a generic side-word
substitution sweep.
"""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

SIDES = ("left", "right")
MIN_CONTROLS = 100


def split_side(name: str):
    for side in SIDES:
        marker = "_" + side
        if name.endswith(marker) and len(name) > len(marker) + 4:
            return name[:-len(marker)], side
    return None


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names("fnv1a_xmaterials")
        if name.strip()
    }
    known.update(
        name.strip().lower().replace("\\", "/")
        for name in snapshot.confirmed_names("material")
        if name.strip()
    )
    grouped = defaultdict(set)
    for name in known:
        parsed = split_side(name)
        if parsed:
            base, side = parsed
            grouped[base].add(side)
    controls = sum(1 for seen in grouped.values() if len(seen) == len(SIDES))
    if controls < MIN_CONTROLS:
        return
    candidates = {
        f"{base}_{side}"
        for base, seen in grouped.items()
        if len(seen) == 1
        for side in SIDES if side not in seen
    }
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
