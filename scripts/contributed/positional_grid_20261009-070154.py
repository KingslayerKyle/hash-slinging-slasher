"""Positional grids: families of same-length names, every token position crossed with every other.

`melee_attack_<outfit>_<weight>_<material>_<pri|alt>_<n>_<hit|miss|fatal>_<npc|plr>` is a grid
whose axes are fixed token positions. Head/tail splits (split_grid) and one-token swaps
(slotswap) each fill one axis at a time; a cell that differs from every known name in two or
more positions is reached by neither.

A family is (directory + first --key tokens, token count). For each family with >= --min names,
each remaining position's token set is collected, and if the product is <= --cap the whole grid
is printed (known names skipped). Families whose positions carry free-form words blow past the
cap and are skipped, which is what keeps this to the genuinely gridded ones.

    python contrib/positional_grid.py | confirm_list - --game BLACKOP7
"""
from pathlib import Path
import argparse
import collections
import itertools
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
MODERN = ("blackop6", "blackop7", "yamyamok", "modwar22", "modwar7")
KINDS = {"image": "fnv1a_ximages_v2", "material": "fnv1a_xmaterials_v2",
         "xanim": "fnv1a_xanims_v2", "sound_alias": "fnv1a_soundbanks_aliases_v2"}


def names(kind):
    f = ROOT / "cod-name-db" / "csv" / (KINDS[kind] + ".csv")
    for line in f.open(encoding="utf-8", errors="replace"):
        yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for g in MODERN:
            for p in (ROOT / top / g).rglob(kind + "*.txt"):
                for line in p.open(encoding="utf-8", errors="replace"):
                    yield line.rstrip("\r\n").partition(",")[2].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", type=int, default=2)
    ap.add_argument("--min", type=int, default=30)
    ap.add_argument("--cap", type=int, default=200000)
    ap.add_argument("--kinds", nargs="+", default=list(KINDS))
    a = ap.parse_args()
    out = sys.stdout.write
    total = 0
    for kind in a.kinds:
        known = {n for n in names(kind) if n and "~" not in n and "&" not in n and "*" not in n}
        fams = collections.defaultdict(list)
        for n in known:
            d, slash, base = n.rpartition("/")
            t = base.split("_")
            if len(t) <= a.key:
                continue
            fams[(d + slash + "_".join(t[:a.key]), len(t))].append(t[a.key:])
        for (key, ln), rows in fams.items():
            if len(rows) < a.min:
                continue
            axes = [sorted({r[i] for r in rows}) for i in range(ln - a.key)]
            size = 1
            for ax in axes:
                size *= len(ax)
            if size > a.cap or size <= len(rows):
                continue
            total += size
            for combo in itertools.product(*axes):
                c = key + "_" + "_".join(combo)
                if c not in known:
                    out(c + "\n")
    print(f"grid cells: {total}", file=sys.stderr)


if __name__ == "__main__":
    main()
