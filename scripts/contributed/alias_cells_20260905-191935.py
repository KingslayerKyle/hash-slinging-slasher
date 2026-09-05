#!/usr/bin/env python3
"""Sound aliases recombined inside the cell the game files them in, not across the whole corpus.

Recombining the named sound corpus against itself is measured dead in both games, under every
shape anybody has tried -- numbered takes, directory x basename, tail swaps, all-boundary cores,
cross-game transfer. Those negatives are total and they are not a plumbing failure: the
vocabulary rebuilds the *known* names almost perfectly and reaches none of the unknown ones.

The reason is that the corpus is not one population. An alias definition table gives every alias
a zone, a bus, a volume group and a duck group, all in plain text, and those four say what the
sound *is*: a zombie map's foley, a warzone announcer line, a menu click. Names inside one such
cell are built from one small vocabulary; names across cells are not related at all. So a
recombination over the whole corpus spends everything it has on pairs that were never going to
go together, which is exactly the shape of a total zero.

This recombines strictly inside a cell. Measured on the tables, cells are tight enough for that
to mean something: of the cells holding both known and unnamed aliases, the single commonest
two-token prefix covers a median 45-48% of the cell, and the best of them are effectively one
family -- 661 unnamed aliases sitting in a cell whose 216 known names share **one** prefix
between them.

A cell's cross product is a cross product, so it is written as a **plan** and handed to the
compiled engine rather than printed -- one plan per cell, since the three lists differ per cell
and that is the whole point of the method.

    python alias_cells.py <aliases.csv> --out plans/cells --top 20
    for p in plans/cells/*.txt: bin\windows\confirm_plan.exe $p

The CSV is the game's alias definition table. Known names come from the published alias tables
and `all_names/`; every id in the table that no name resolves is what the cell is being mined for.
"""
import argparse
import collections
import csv
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASK = (1 << 63) - 1
BASIS = 0xCBF29CE484222325
PRIME = 0x100000001B3
U64 = (1 << 64) - 1

# What the game files a sound under. Zone is the bank, volume group and duck group are what kind
# of sound it is; together they are a far better predictor of a name than the corpus at large.
CELL = ("zone", "volumegroup", "duckgroup")


def fnv1a63(s):
    x = BASIS
    for c in s.lower().replace("\\", "/").encode("utf-8", "replace"):
        x = ((x ^ c) * PRIME) & U64
    return x & MASK


def known_names():
    out = {}
    for f in ("fnv1a_soundbanks_aliases.csv", "fnv1a_soundbanks_aliases_v2.csv"):
        p = os.path.join(ROOT, "cod-name-db", "csv", f)
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    parts = line.strip().split(",", 1)
                    if len(parts) == 2 and parts[1]:
                        out[fnv1a63(parts[1])] = parts[1]
    for g in ("blkops04", "blkopscw"):
        p = os.path.join(ROOT, "all_names", g, "sound_alias.txt")
        if os.path.exists(p):
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    nm = line.strip().split(",")[-1]
                    if nm:
                        out[fnv1a63(nm)] = nm
    return out


def parts(names, depth):
    """Heads, cores and tails of a cell's names, each cut at whole-token boundaries."""
    heads, cores, tails = collections.Counter(), collections.Counter(), collections.Counter()
    for nm in names:
        t = nm.split("_")
        for k in range(1, min(depth, len(t) - 1) + 1):
            heads["_".join(t[:k])] += 1
            tails["_".join(t[-k:])] += 1
        for i in range(1, len(t)):
            for j in range(i + 1, min(i + depth, len(t)) + 1):
                cores["_".join(t[i:j])] += 1
    return heads, cores, tails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--out", default="plans/cells", help="directory to write the plans into")
    ap.add_argument("--top", type=int, default=20, help="how many cells to write, by unnamed count")
    ap.add_argument("--depth", type=int, default=3, help="max tokens in a head, core or tail")
    ap.add_argument("--axis", type=int, default=3000, help="max entries kept per axis")
    ap.add_argument("--min-known", type=int, default=4)
    args = ap.parse_args()

    known = known_names()
    cells = collections.defaultdict(lambda: [set(), set()])
    with open(args.csv, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            n = (row.get("name") or "").strip()
            if not n:
                continue
            a = int(n, 16) & MASK
            key = tuple((row.get(c) or "").strip() for c in CELL)
            nm = known.get(a)
            if nm:
                cells[key][0].add(nm)
            else:
                cells[key][1].add(a)

    live = [(len(u), k) for k, (kn, u) in cells.items() if u and len(kn) >= args.min_known]
    live.sort(reverse=True)
    print("cells: %d total, %d worth mining, %d unnamed ids in them"
          % (len(cells), len(live), sum(n for n, _ in live)), file=sys.stderr)

    os.makedirs(args.out, exist_ok=True)
    written = 0
    for n_unnamed, key in live[: args.top]:
        heads, cores, tails = parts(cells[key][0], args.depth)
        hs = [h for h, _ in heads.most_common(args.axis)]
        cs = [c for c, _ in cores.most_common(args.axis * 4)]
        ts = [t for t, _ in tails.most_common(args.axis)]
        if not (hs and cs and ts):
            continue
        slug = re.sub(r"[^a-z0-9]+", "_", "_".join(key).lower()).strip("_")[:60]
        base = os.path.join(args.out, slug)
        rel = base.replace(os.sep, "/")
        for suffix, axis in (("heads", hs), ("cores", cs), ("tails", ts)):
            with open("%s.%s.txt" % (base, suffix), "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(axis) + "\n")
        with open("%s.txt" % base, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("label: alias cell %s\n" % " / ".join(key))
            fh.write("describe: sound aliases recombined only against the other aliases the game "
                     "files in the same zone, volume group and duck group -- %d known names in "
                     "this cell, %d ids in it still unnamed\n\n"
                     % (len(cells[key][0]), n_unnamed))
            fh.write("begin: @%s.heads.txt\n" % rel)
            fh.write("stem:  @%s.cores.txt\n" % rel)
            fh.write("end:   @%s.tails.txt\n\n" % rel)
            fh.write("bare: no\nfold: yes\n")
        written += 1
        print("  %-52s %6d unnamed  %5d known  %d x %d x %d"
              % (slug, n_unnamed, len(cells[key][0]), len(hs), len(cs), len(ts)), file=sys.stderr)
    print("wrote %d plans into %s" % (written, args.out), file=sys.stderr)


if __name__ == "__main__":
    main()
