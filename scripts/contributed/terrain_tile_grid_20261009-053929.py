"""Terrain-tile materials filled out on their own coordinate lattice.

`tm7/saba_-59_-40_0_2`, `tm7p/jup_bigmap_9_-59_1_2`: a terrain material is <dir>/<map>_<x>_<y>
plus a short `_a_b` suffix, and x/y are not arbitrary -- they are floor(k * step) for one step per
map: 9.765625 (10000/1024) on saba/jup_bigmap/jup_chemical (..., -20, -10, 0, 9, 19, 29, 39, 48,
...), 19.53125 on saba2, 8 on sealion. A table holds the tiles somebody happened to export, so the
lattice has holes, and every hole is a candidate.

Per (dir, map) family: the step is the candidate that explains the most observed coordinates,
the lattice runs from the observed min to max widened by --pad steps, every x and y on it is
crossed with every suffix the family (and its map in any dir) carries, and the whole tile set is
also tried under every sibling terrain directory the map appears in elsewhere plus the core ones.

    python contrib/terrain_tile_grid.py | confirm_list - --game BLACKOP7
"""
from pathlib import Path
import argparse
import collections
import math
import re

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
PAT = re.compile(r"^([#~]?tm[a-z0-9]*/)(.+?)_(-?\d+)_(-?\d+)((?:_\d+)*)$")
STEPS = sorted({10000 / 1024 * f for f in (0.25, 0.5, 1, 2, 4, 8)} |
               {24000 / 1024, 15.625, 31.25, 46.875} | set(range(1, 65)))
CORE_DIRS = ("tm7/", "tm7p/", "tm/", "tmo/", "~tm/", "tml8/", "tm9/", "tml/", "#tm7/", "tm8/")


def names():
    srcs = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_xmaterials*.csv"))
    for top in ("all_names", "findings", "submissions"):
        srcs += list((ROOT / top).rglob("material*.txt"))
    for f in srcs:
        for line in f.open(encoding="utf-8", errors="replace"):
            n = line.rstrip("\r\n").partition(",")[2].lower()
            if "tm" in n[:5]:
                yield n


LATTICES = {s: {math.floor(k * s) for k in range(-1000, 1001)} for s in STEPS if s >= 4}


def lattice(coords, pad, cap=60):
    """The largest step that explains >= 90% of the observed coordinates, filled out; a family
    with no such step keeps only what it observed (a step of 1 'explains' anything)."""
    best = None
    for s, on in LATTICES.items():
        if sum(c in on for c in coords) >= 0.9 * len(coords) and (best is None or s > best):
            best = s
    if best is None:
        return sorted(coords)
    lo = math.floor(min(coords) / best) - pad
    hi = math.ceil(max(coords) / best) + pad
    axis = sorted({math.floor(k * best) for k in range(lo, hi + 1)} | set(coords))
    return axis if len(axis) <= cap else sorted(coords)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", type=int, default=2)
    a = ap.parse_args()
    known = set(names())
    fam = collections.defaultdict(lambda: [set(), set()])
    map_dirs, map_sfx = collections.defaultdict(set), collections.defaultdict(set)
    for n in known:
        m = PAT.match(n)
        if not m:
            continue
        d, mp, x, y, s = m.groups()
        fam[(d, mp)][0].update((int(x), int(y)))
        map_dirs[mp].add(d)
        map_sfx[mp].add(s)
    seen = set()
    for (d, mp), (coords, _) in sorted(fam.items()):
        if len(coords) < 2:
            continue
        axis = lattice(coords, a.pad)
        dirs = map_dirs[mp] | set(CORE_DIRS)
        for dd in sorted(dirs):
            if (dd, mp) in seen:
                continue
            seen.add((dd, mp))
            for x in axis:
                for y in axis:
                    for s in sorted(map_sfx[mp]):
                        c = f"{dd}{mp}_{x}_{y}{s}"
                        if c not in known:
                            print(c)


if __name__ == "__main__":
    main()
