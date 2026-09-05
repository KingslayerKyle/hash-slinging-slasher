#!/usr/bin/env python3
"""Fill BO4 operator-cosmetic material terminal `_exo1`/`_exo2` mirrors.

Only `mc/mtl_c_t8_mp_spe_` materials qualify.  The whole base is held fixed
and the relation requires 100 complete same-base controls, so it cannot become
a generic numeric-family sweep.
"""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

PREFIX = "mc/mtl_c_t8_mp_spe_"
ENDS = ("exo1", "exo2")
MIN_CONTROLS = 100


def split_exo(name: str):
    if not name.startswith(PREFIX):
        return None
    for ending in ENDS:
        marker = "_" + ending
        if name.endswith(marker):
            return name[:-len(marker)], ending
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
        parsed = split_exo(name)
        if parsed:
            base, ending = parsed
            grouped[base].add(ending)
    controls = sum(1 for seen in grouped.values() if len(seen) == len(ENDS))
    if controls < MIN_CONTROLS:
        return
    candidates = {
        f"{base}_{ending}"
        for base, seen in grouped.items()
        if len(seen) == 1
        for ending in ENDS if ending not in seen
    }
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
