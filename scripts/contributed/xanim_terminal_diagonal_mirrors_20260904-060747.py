#!/usr/bin/env python3
"""Fill high-control terminal diagonal-direction mirrors in real xanims.

Only `_fl`/`_fr` and `_bl`/`_br` qualify; each direction pair must have at
least 100 complete same-base controls.  This is a terminal spelling mirror,
not a stance/action grid.
"""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

PAIRS = (("fl", "fr"), ("bl", "br"))
MIN_CONTROLS = 100


def split_direction(name: str):
    for left, right in PAIRS:
        for direction in (left, right):
            marker = "_" + direction
            if name.endswith(marker) and len(name) > len(marker) + 4:
                return name[:-len(marker)], (left, right), direction
    return None


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names("fnv1a_xanims")
        if name.strip()
    }
    known.update(
        name.strip().lower().replace("\\", "/")
        for name in snapshot.confirmed_names("xanim")
        if name.strip()
    )
    grouped = defaultdict(set)
    for name in known:
        parsed = split_direction(name)
        if parsed:
            base, pair, direction = parsed
            grouped[(base, pair)].add(direction)
    controls = {
        pair: sum(1 for (base, candidate_pair), seen in grouped.items()
                  if candidate_pair == pair and len(seen) == 2)
        for pair in PAIRS
    }
    candidates = {
        f"{base}_{direction}"
        for (base, pair), seen in grouped.items()
        if controls[pair] >= MIN_CONTROLS and len(seen) == 1
        for direction in pair if direction not in seen
    }
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
