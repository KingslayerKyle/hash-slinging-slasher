#!/usr/bin/env python3
"""Fill strongly attested same-core terminal channel counterparts in ``amb_``.

Only the exact L/R and LR/LSRS terminal pairs are considered.  A pair must
have twenty complete full-name controls before a missing same-core side is
emitted; this deliberately cannot turn into a free channel cross product.
"""
from collections import defaultdict
from pathlib import Path
import sys

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

PAIRS = (("l", "r"), ("lr", "lsrs"))
MIN_CONTROLS = 20


def split_channel(name: str):
    if not name.startswith("amb_"):
        return None
    for left, right in PAIRS:
        for channel in (left, right):
            marker = "_" + channel
            if name.endswith(marker) and len(name) > len(marker) + 4:
                return name[:-len(marker)], (left, right), channel
    return None


def main() -> None:
    known = {
        name.strip().lower().replace("\\", "/")
        for name in snapshot.table_names("fnv1a_soundbanks_aliases")
        if name.strip()
    }
    known.update(
        name.strip().lower().replace("\\", "/")
        for name in snapshot.confirmed_names("sound_alias")
        if name.strip()
    )
    grouped = defaultdict(set)
    for name in known:
        parsed = split_channel(name)
        if parsed:
            base, pair, channel = parsed
            grouped[(base, pair)].add(channel)
    controls = {
        pair: sum(1 for (base, candidate_pair), seen in grouped.items()
                  if candidate_pair == pair and len(seen) == 2)
        for pair in PAIRS
    }
    candidates = {
        f"{base}_{channel}"
        for (base, pair), seen in grouped.items()
        if controls[pair] >= MIN_CONTROLS and len(seen) == 1
        for channel in pair if channel not in seen
    }
    print("\n".join(sorted(candidates)))


if __name__ == "__main__":
    main()
