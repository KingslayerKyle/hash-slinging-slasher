#!/usr/bin/env python3
"""Fill terminal `_view`/`_world` xmodel mirrors from recovered CW xmodels."""
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "all_names" / "blkopscw" / "xmodel.txt"
ENDS = ("view", "world")
MIN_CONTROLS = 50


def split_end(name: str):
    for ending in ENDS:
        marker = "_" + ending
        if name.endswith(marker) and len(name) > len(marker) + 4:
            return name[:-len(marker)], ending
    return None


def main() -> None:
    known = set()
    for line in SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines():
        _, _, name = line.partition(",")
        if name:
            known.add(name.strip().lower().replace("\\", "/"))
    grouped = defaultdict(set)
    for name in known:
        parsed = split_end(name)
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
