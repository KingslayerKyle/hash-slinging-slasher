#!/usr/bin/env python3
"""Sound aliases named from the aliases they point at.

Both games' alias definition tables carry, for every alias, the other aliases it refers to:
`secondaryaliasname` (the alias played alongside it) and `stopalias` (the alias that stops it).
Those columns are hashes, so they name nothing on their own -- but they are *edges*, and an edge
with a known name at one end and an unknown at the other is a name we are one guess away from.

That is the thing the standing sound negatives said was missing. Recombining the named sound
corpus against itself is measured dead in both games, under every shape tried: numbered takes,
directory x basename, tail swaps, all-boundary cores. All of them fail the same way, because the
named aliases are not a random sample of the pool and the unnamed ones are not built from their
pieces. An edge is different: it does not ask what the corpus looks like in general, it says
*this specific unknown alias is the partner of this specific known one*, on the game's own
authority.

The edit that turns one end of an edge into the other is not guessed either. The same tables hold
tens of thousands of edges with a known name at **both** ends, and every one of those is a worked
example:

    mpl_hud_notify_camo        ->  mpl_hud_notify_camo_riff
    wpn_flame_thrower_start_plr->  wpn_flame_thrower_cooldown
    uin_aar_bar_fill_tail      ->  uin_aar_bar_fill_main
    tst_front_left_1           ->  tst_front_right_1

So the grammar is measured from the closed edges and applied to the open ones. A rule is the pair
of tails that differ after the longest shared run of whole tokens, which covers appending,
replacing and swapping in one form.

    python alias_edges.py <aliases.csv> --game BLKOPS04 | confirm_list - --game BLKOPS04

The CSV is the game's alias definition table: a `name` column and the reference columns, each
holding a 64-bit hash. Known names are read from the published alias tables and `all_names/`.
"""
import argparse
import collections
import csv
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASK = (1 << 63) - 1
BASIS = 0xCBF29CE484222325
PRIME = 0x100000001B3
U64 = (1 << 64) - 1

# The columns that hold another alias's hash. `chainaliasname` is in the header of both games'
# tables and is empty in every row of both, so it is listed and costs nothing.
EDGE_COLUMNS = ("secondaryaliasname", "chainaliasname", "stopalias")


def fnv1a63(s):
    x = BASIS
    for c in s.lower().replace("\\", "/").encode("utf-8", "replace"):
        x = ((x ^ c) * PRIME) & U64
    return x & MASK


def known_names():
    """Every alias name anybody holds, by id. Both games, since aliases cross between them."""
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


def rule(a, b):
    """The (from-tail, to-tail) pair left after the longest shared run of whole tokens.

    Whole tokens rather than characters, so `..._camo` -> `..._camo_riff` yields ("", "_riff")
    and not ("o", "o_riff"). Returning the tails rather than a diff is what lets the rule be
    replayed onto a different name that ends the same way.
    """
    ta, tb = a.split("_"), b.split("_")
    i = 0
    while i < len(ta) and i < len(tb) and ta[i] == tb[i]:
        i += 1
    if i == 0:
        return None
    fa, fb = "_".join(ta[i:]), "_".join(tb[i:])
    return ("_" + fa if fa else "", "_" + fb if fb else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", help="the game's alias definition table")
    ap.add_argument("--min-rule", type=int, default=2,
                    help="how many closed edges a rule must be seen on to be replayed")
    args = ap.parse_args()

    known = known_names()
    print("known alias names: %d" % len(known), file=sys.stderr)

    closed = collections.Counter()
    open_edges = set()
    with open(args.csv, encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            n = (row.get("name") or "").strip()
            if not n:
                continue
            a = int(n, 16) & MASK
            for col in EDGE_COLUMNS:
                v = (row.get(col) or "").strip()
                if not v:
                    continue
                b = int(v, 16) & MASK
                ka, kb = known.get(a), known.get(b)
                if ka and kb:
                    r = rule(ka, kb)
                    if r:
                        closed[r] += 1
                    r = rule(kb, ka)
                    if r:
                        closed[r] += 1
                elif ka and not kb:
                    open_edges.add(ka)
                elif kb and not ka:
                    open_edges.add(kb)

    rules = [r for r, c in closed.most_common() if c >= args.min_rule]
    print("closed edges give %d distinct rules, %d kept at >=%d sightings"
          % (len(closed), len(rules), args.min_rule), file=sys.stderr)
    print("open edges anchored on a known name: %d" % len(open_edges), file=sys.stderr)

    # An added tail that never replaces anything is worth trying on every anchor, not only on the
    # ones already ending in its rule's from-tail: appending is the commonest edge in both tables.
    appends = sorted({to for frm, to in rules if frm == "" and to})

    n = 0
    seen = set()
    for anchor in sorted(open_edges):
        cands = []
        for frm, to in rules:
            if frm and anchor.endswith(frm):
                cands.append(anchor[: len(anchor) - len(frm)] + to)
        cands.extend(anchor + t for t in appends)
        for c in cands:
            if c and c not in seen:
                seen.add(c)
                n += 1
                print(c)
    print("emitted %d" % n, file=sys.stderr)


if __name__ == "__main__":
    main()
