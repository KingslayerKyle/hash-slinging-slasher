"""Every alias family completed as a grid of its middle against its final token.

Generalises `operator_vo_grid.py`, which returned 7,657 new names from 12,420 candidates across
MWII, MWIII and BO7. A family is the aliases sharing their first `--head` tokens and their token
count; within it, every attested middle (the tokens between head and last) is crossed with every
attested final token. Families whose grid would exceed `--cap` cells, or whose final token takes
fewer than `--min-last` values, are skipped -- a big sparse family is a list, not a grid.

Spent by: the alias corpus as it stands; re-run after any alias batch (it snowballs).
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')


def aliases():
    sources = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_soundbanks_aliases*.csv"))
    for folder in ("submissions", "findings", "all_names"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("sound_alias*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower()
            if name and "/" not in name and "\\" not in name:
                yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", type=int, default=2)
    ap.add_argument("--cap", type=int, default=200_000)
    ap.add_argument("--min-last", type=int, default=3)
    args = ap.parse_args()

    middles, lasts = defaultdict(set), defaultdict(set)
    for name in set(aliases()):
        tokens = name.split("_")
        if len(tokens) < args.head + 2:
            continue
        family = ("_".join(tokens[:args.head]), len(tokens))
        middles[family].add("_".join(tokens[args.head:-1]))
        lasts[family].add(tokens[-1])

    families = cells = 0
    for family in sorted(middles):
        m, l = middles[family], lasts[family]
        size = len(m) * len(l)
        if len(l) < args.min_last or len(m) < 2 or size > args.cap:
            continue
        families += 1
        cells += size
        head = family[0]
        for middle in sorted(m):
            for last in sorted(l):
                print(f"{head}_{middle}_{last}")
    print(f"{families:,} families, {cells:,} cells", file=sys.stderr)


if __name__ == "__main__":
    main()
