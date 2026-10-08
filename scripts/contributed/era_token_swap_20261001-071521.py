"""Translate one game's names into the other's, one learned token swap at a time.

Cold War carries a great deal of Black Ops 4's content, but rarely under the identical name --
the verbatim cross-game transfer returned 3 names from 702,081. What changes between the two is
usually one token: `t8` for `t9`, a renamed map code, a reworked weapon codename. Those swaps can be
*measured* rather than guessed: index every name present in game B by "its tokens with one slot
blanked", look every name present in game A up under the same blanks, and every hit is a pair of
real names that differ in exactly one slot -- one token in A, another in B.

Counted over both games' whole named sets, the pairs that recur are the translation table. This
then applies the top swaps to every name present in A whose translated form is not already named in
B, and prints the result for `confirm_list --game B`.

What it reaches that slotswap and token_edits do not: those substitute a slot with any word the
corpus has seen in that context, inside one game. This substitutes only with swaps evidenced
*across* the two games, and only on names proven real in the other one.

    python contrib/era_token_swap.py --source BLKOPS04 --target BLKOPSCW --top 3000 \
        | bin\\windows\\confirm_list.exe - --game BLKOPSCW --label "era token swap" \
          --script contrib/era_token_swap.py
    python contrib/era_token_swap.py ... --stats         the learned table and the size, nothing else
"""
import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402

POOLS = ("xmodel", "xanim", "image", "material", "sound_alias")
MASK = (1 << 63) - 1
SPLIT = re.compile(r"([_/])")
# Image names often end in an 8-hex-digit hash of their own content; swapping one for another is
# noise that the pair count rewards, so such tokens never enter the table.
HEXISH = re.compile(r"^(?=.*\d)[0-9a-f]{6,}$")


def all_names():
    import glob
    folder = snapshot.settings.tables_csv()
    names = set()
    for path in glob.glob(os.path.join(folder, "*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                name = name.strip().lower().replace("\\", "/")
                if name:
                    names.add(name)
    for name in snapshot.confirmed_names():
        names.add(name.strip().lower().replace("\\", "/"))
    return names


def game_ids(game):
    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        if snap.game == game:
            return {pool: {i & MASK for i in ids} for pool, ids in snap.by_pool().items() if pool in POOLS}
    raise SystemExit("no snapshot for %s" % game)


def present(names, ids):
    """{pool: set(names)} of names whose hash is an id of that pool."""
    lookup = {}
    for pool, members in ids.items():
        for i in members:
            lookup[i] = pool
    out = collections.defaultdict(set)
    for name in names:
        pool = lookup.get(snapshot.fnv1a(name) & MASK)
        if pool:
            out[pool].add(name)
    return out


def blanks(name):
    parts = SPLIT.split(name)
    for i in range(0, len(parts), 2):
        if parts[i]:
            yield "".join(parts[:i]) + "\0" + "".join(parts[i + 1:]), parts[i], i, parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--top", type=int, default=3000)
    ap.add_argument("--min", type=int, default=3, help="a swap must be evidenced this many times")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    names = all_names()
    src = present(names, game_ids(args.source))
    tgt_ids = game_ids(args.target)
    tgt = present(names, tgt_ids)
    tgt_all = {i for s in tgt_ids.values() for i in s}

    pairs = collections.Counter()
    for pool in POOLS:
        index = collections.defaultdict(set)
        for name in tgt[pool]:
            for key, tok, _, _ in blanks(name):
                index[key].add(tok)
        for name in src[pool]:
            for key, tok, _, _ in blanks(name):
                for other in index.get(key, ()):
                    if other != tok:
                        pairs[(pool, tok, other)] += 1

    # A swap that also links siblings *inside* the target is just a family variant (01 -> 02),
    # which slotswap already owns. Keep the ones that are evidence of a cross-game respelling.
    inside = collections.Counter()
    for pool in POOLS:
        index = collections.defaultdict(set)
        for name in tgt[pool]:
            for key, tok, _, _ in blanks(name):
                index[key].add(tok)
        for toks in index.values():
            if 1 < len(toks) < 40:
                for a in toks:
                    for b in toks:
                        if a != b:
                            inside[(pool, a, b)] += 1

    scored = []
    for key, n in pairs.items():
        if n < args.min or HEXISH.match(key[1]) or HEXISH.match(key[2]):
            continue
        scored.append((n / (1 + inside.get(key, 0)), n, key))
    scored.sort(reverse=True)
    table = collections.defaultdict(list)
    for _, _, (pool, a, b) in scored[: args.top]:
        table[(pool, a)].append(b)

    if args.stats:
        for s, n, key in scored[:60]:
            print("%8.2f %6d %s" % (s, n, key), file=sys.stderr)

    seen = set()
    count = 0
    for pool in POOLS:
        for name in src[pool]:
            if snapshot.fnv1a(name) & MASK in tgt_all:
                continue
            for _, tok, i, parts in blanks(name):
                for other in table.get((pool, tok), ()):
                    cand = "".join(parts[:i]) + other + "".join(parts[i + 1:])
                    if cand in seen:
                        continue
                    seen.add(cand)
                    count += 1
                    if not args.stats:
                        sys.stdout.write(cand + "\n")
    print("%d swaps kept, %d candidates" % (len(scored[: args.top]), count), file=sys.stderr)


if __name__ == "__main__":
    main()
