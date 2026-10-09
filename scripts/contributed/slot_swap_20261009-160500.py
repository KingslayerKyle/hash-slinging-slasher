"""One token of a name swapped for every value its siblings take in that slot, keeping each tail.

For a beginning P (the first i tokens of a name), the slot is token i and W(P) the values it takes
across every known name starting with P; each value w carries tails T(P, w) (the tokens after the
slot). The candidates are P + w' + t for every w' in W(P) and t in the union of T(P, *): a weapon,
operator or map codename sitting at a fixed depth gets every action any sibling has. It differs
from `alias_heads_shared_tails` (any head x tails shared by >= N heads) by keeping the beginning
fixed, so a tail attested once under one sibling still transfers, and from `family_grid_modern`
(middle x final token) by moving the slot to the front instead of the end.

    python contrib/slot_swap.py --kind image --game blackop7 > cands.txt

Spent by: the corpus of the kind given as it stands; re-run after it grows (it snowballs).
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent
TABLES = {"image": "fnv1a_ximages*.csv", "material": "fnv1a_xmaterials*.csv",
          "sound_alias": "fnv1a_soundbanks_aliases*.csv", "xanim": "fnv1a_xanims*.csv", "sound_asset": "fnv1a_xsounds_v2.csv"}


def names(kind):
    srcs = list((ROOT / "cod-name-db" / "csv").glob(TABLES[kind]))
    for folder in ("findings", "submissions"):
        srcs += list((ROOT / folder).rglob(f"{kind}*.txt"))
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            v = (v if sep else k).strip().lower()
            if v and "~" not in v and "," not in v:
                yield v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", default="image")
    ap.add_argument("--max-slot", type=int, default=400, help="skip slots with more values")
    ap.add_argument("--max-tails", type=int, default=3000)
    ap.add_argument("--min-slot", type=int, default=2)
    ap.add_argument("--count", action="store_true")
    a = ap.parse_args()
    known = set(names(a.kind))
    groups = defaultdict(lambda: defaultdict(set))   # P -> w -> tails
    for n in known:
        t = n.split("_")
        for i in range(1, len(t) - 1):
            groups["_".join(t[:i]) + "_"][t[i]].add("_".join(t[i + 1:]))
    total = 0
    out = sys.stdout
    for p, ws in groups.items():
        if not a.min_slot <= len(ws) <= a.max_slot:
            continue
        tails = set().union(*ws.values())
        if len(tails) > a.max_tails:
            continue
        total += len(ws) * len(tails)
        if a.count:
            continue
        for w in ws:
            for tl in tails:
                c = f"{p}{w}_{tl}"
                if c not in known:
                    out.write(c + "\n")
    print(f"{len(known):,} names, {total:,} cells", file=sys.stderr)


if __name__ == "__main__":
    main()
