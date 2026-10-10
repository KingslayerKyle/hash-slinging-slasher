"""One interior token of a known name replaced by every token seen between the same two neighbours.

For a name `a_b_c`, the context of `b` is the pair (`a`, `c`). Every token any known name of the
kind carries between that same pair is a value the slot is attested to take, so each is offered in
place of `b`, keeping the whole rest of the name. Unlike `slot_swap` (fixed beginning, every tail
of every sibling) this keeps the entire name and changes one word, which is the shape of a variant:
`..._left_hand_...` / `..._right_hand_...`, `..._door_open_02` / `..._door_close_02`. The idea came
from a parallel BLACKOP6 worker (+963 there on its first run).

    python contrib/context_swap.py --kind material | confirm_list - --game <TAG> --script contrib/context_swap.py

Spent by: the corpus of the kind as it stands; re-run after it grows (it snowballs).
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
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
    ap.add_argument("--max-values", type=int, default=300, help="skip contexts with more values")
    ap.add_argument("--dotted", action="store_true", help="also print '/' spelled as '.'")
    a = ap.parse_args()
    known = set(names(a.kind))
    split = [n.split("_") for n in known]
    ctx = defaultdict(set)
    for t in split:
        for i in range(1, len(t) - 1):
            ctx[(t[i - 1], t[i + 1])].add(t[i])
    out, total = sys.stdout, 0
    for t in split:
        for i in range(1, len(t) - 1):
            vals = ctx[(t[i - 1], t[i + 1])]
            if len(vals) < 2 or len(vals) > a.max_values:
                continue
            for v in vals:
                if v == t[i]:
                    continue
                c = "_".join(t[:i] + [v] + t[i + 1:])
                if c in known:
                    continue
                total += 1
                out.write(c + "\n")
                if a.dotted and "/" in c:
                    out.write(c.replace("/", ".") + "\n")
    print(f"{len(known):,} names, {total:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
