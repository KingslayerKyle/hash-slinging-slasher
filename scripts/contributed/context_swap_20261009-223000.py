"""Each interior token swapped for every token seen between the same two neighbours.

From the BO6 worker (+963 there). For every known name of a kind, interior token t[i] has the
context (t[i-1], t[i+1]); every token seen in that context anywhere in the corpus is a value of it.
Each name is offered with t[i] replaced by every other value of its context. Contexts with more
than `--max-values` values are skipped (they are function words, not slots).

    python contrib/context_swap.py --kind image

Spent by: the corpus of the kind as it stands; re-run after it grows (it snowballs).
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent
TABLES = {"image": "fnv1a_ximages*.csv", "material": "fnv1a_xmaterials*.csv", "xanim": "fnv1a_xanims*.csv",
          "sound_alias": "fnv1a_soundbanks_aliases*.csv", "sound_asset": "fnv1a_xsounds_v2.csv"}


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
    ap.add_argument("--max-values", type=int, default=300)
    a = ap.parse_args()
    known = set(names(a.kind))
    ctx = defaultdict(set)
    toks = [n.split("_") for n in known]
    for t in toks:
        for i in range(1, len(t) - 1):
            ctx[(t[i - 1], t[i + 1])].add(t[i])
    n = 0
    out = sys.stdout
    for t in toks:
        for i in range(1, len(t) - 1):
            vals = ctx[(t[i - 1], t[i + 1])]
            if len(vals) < 2 or len(vals) > a.max_values:
                continue
            for v in vals:
                if v != t[i]:
                    c = "_".join(t[:i] + [v] + t[i + 1:])
                    if c not in known:
                        out.write(c + "\n")
                        n += 1
    print(f"{len(known):,} names, {n:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
