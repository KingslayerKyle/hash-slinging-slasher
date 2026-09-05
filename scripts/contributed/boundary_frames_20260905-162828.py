#!/usr/bin/env python3
"""The heads and tails a name wears around one token, cut at every boundary.

`heads` and `tails` cut a name once and keep one side. This keeps both sides of the *same* cut,
so what comes out is a frame: everything before some token, and everything after it. Cross a
frame's two halves with a vocabulary of single tokens and you are asking the question those two
methods cannot -- not "what else begins like this" or "what else ends like this", but "what else
goes *here*".

That is only worth asking with tokens the corpus does not already carry, which is what
`untargeted_pool_cores.py` produces: words that are real in these games because an fx, an ai type
or a vehicle is named after them, and that no model, material or image name we hold has ever
used. A frame harvested from `..._zm_platinum_trash_debris_02` and a token harvested from a beam
called `beam8_zm_scepter` together propose a name neither source contains.

    python boundary_frames.py --heads > heads.txt
    python boundary_frames.py --tails > tails.txt

Both are ranked by how many distinct names wear them, and `--limit` caps each list so a plan
stays inside the night it has. Cuts are taken at every underscore, slash and dot, so a frame can
sit five segments deep.
"""
import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The published tables that describe these two titles. The `_v2` tables are the newer engines and
# are measured dead against both games, so they are not read here.
TABLES = (
    "fnv1a_xmodels.csv", "fnv1a_ximages.csv", "fnv1a_xmaterials.csv", "fnv1a_xanims.csv",
)
BOUNDARY = re.compile(r"[_/\\.]")


def held_names(game):
    """Every name that describes this game: what we confirmed, plus the era's published tables."""
    d = os.path.join(ROOT, "all_names", game)
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            if f.endswith(".txt"):
                with open(os.path.join(d, f), encoding="utf-8", errors="replace") as fh:
                    for line in fh:
                        nm = line.strip().split(",", 1)[-1]
                        if nm:
                            yield nm.lower()
    for f in TABLES:
        p = os.path.join(ROOT, "cod-name-db", "csv", f)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                nm = line.strip().split(",", 1)[-1]
                if nm:
                    yield nm.lower()


def frames(name):
    """Every (head, tail) pair produced by lifting one whole token out of the name.

    The head keeps its trailing separator and the tail keeps its leading one, so head + token +
    tail reassembles the original exactly -- which is what makes the list verifiable: rebuild a
    known name from its own frame and you know the cut is sound.
    """
    cuts = [m.start() for m in BOUNDARY.finditer(name)]
    for a, b in zip(cuts, cuts[1:]):
        yield name[:a + 1], name[b:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=None, help="all_names subdirectory; default reads state")
    ap.add_argument("--heads", action="store_true")
    ap.add_argument("--tails", action="store_true")
    ap.add_argument("--limit", type=int, default=40000)
    ap.add_argument("--min-count", type=int, default=2)
    args = ap.parse_args()

    game = args.game
    if not game:
        p = os.path.join(ROOT, "state", "game.txt")
        game = open(p).read().strip().lower() if os.path.exists(p) else "blkopscw"

    heads = collections.Counter()
    tails = collections.Counter()
    n = 0
    for nm in held_names(game):
        n += 1
        for h, t in frames(nm):
            heads[h] += 1
            tails[t] += 1
    print("names read: %d" % n, file=sys.stderr)
    print("distinct heads: %d, tails: %d" % (len(heads), len(tails)), file=sys.stderr)

    want = heads if args.heads else tails
    kept = [s for s, c in want.most_common() if c >= args.min_count][: args.limit]
    print("emitting %d" % len(kept), file=sys.stderr)
    for s in kept:
        print(s)


if __name__ == "__main__":
    main()
