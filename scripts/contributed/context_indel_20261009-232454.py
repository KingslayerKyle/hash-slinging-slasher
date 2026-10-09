"""One token inserted into, or deleted from, a known name wherever its neighbours attest the change.

Insert: two adjacent tokens `a_b` get `a_x_b` for every `x` the corpus carries between `a` and `b`
in some other name. Delete: `a_x_b` loses `x` when the corpus has `a` and `b` adjacent somewhere.
That is the shape of optional words -- `..._door_wood_open_...` / `..._door_open_...`, a `_vm_` or
`_mp_` present in one family and absent from its sibling. The idea came from a parallel BLACKOP6
worker (+632 there on its first run).

    python contrib/context_indel.py --kind material | confirm_list - --game <TAG> --script contrib/context_indel.py

Spent by: the corpus of the kind as it stands; re-run after it grows (it snowballs).
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent
TABLES = {"image": "fnv1a_ximages*.csv", "material": "fnv1a_xmaterials*.csv",
          "sound_alias": "fnv1a_soundbanks_aliases*.csv", "xanim": "fnv1a_xanims*.csv",
          "sound_asset": "fnv1a_xsounds_v2.csv"}


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
    ap.add_argument("--max-values", type=int, default=200, help="skip gaps with more insertable tokens")
    ap.add_argument("--dotted", action="store_true", help="also print '/' spelled as '.'")
    a = ap.parse_args()
    known = set(names(a.kind))
    split = [n.split("_") for n in known]
    between = defaultdict(set)   # (a, b) -> tokens seen between them
    adjacent = set()
    for t in split:
        for i in range(len(t) - 1):
            adjacent.add((t[i], t[i + 1]))
        for i in range(1, len(t) - 1):
            between[(t[i - 1], t[i + 1])].add(t[i])
    out, total = sys.stdout, 0

    def emit(c):
        nonlocal total
        if c in known:
            return
        total += 1
        out.write(c + "\n")
        if a.dotted and "/" in c:
            out.write(c.replace("/", ".") + "\n")

    for t in split:
        for i in range(len(t) - 1):
            xs = between.get((t[i], t[i + 1]), ())
            if len(xs) <= a.max_values:
                for x in xs:
                    emit("_".join(t[:i + 1] + [x] + t[i + 1:]))
        for i in range(1, len(t) - 1):
            if (t[i - 1], t[i + 1]) in adjacent:
                emit("_".join(t[:i] + t[i + 1:]))
    print(f"{len(known):,} names, {total:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
