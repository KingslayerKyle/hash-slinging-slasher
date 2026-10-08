r"""Names in probability order under a token trigram model of one game's own named assets.

Every generator here is a cross product of lists, or an edit of one known name. Neither can write a
name whose *start* comes from one family and whose *end* comes from another unless the lists happen
to be cut at the right boundary. `continuations.py` comes closest, offering a whole known prefix the
tokens that followed it -- but its context is the whole prefix, so it only ever extends names that
already exist up to that point.

This borrows the shape password crackers settled on (OMEN, Markov enumeration): learn
P(token | previous two tokens) over every name the game is known to hold in one pool, then
enumerate every token sequence whose probability clears a threshold, best first, by depth-first
search with pruning. The context is short, so a walk can pass from one family into another
wherever the two share a two-token seam -- which is exactly where real names are spliced.

Trained per game and per pool on names *present in that game*, so it speaks that game's dialect,
not the published tables' average.

    python contrib/token_markov.py --game BLKOPSCW --pool image --budget 5000000 \
        | bin\windows\confirm_list.exe - --game BLKOPSCW --label "token trigram walk" \
          --script contrib/token_markov.py
"""
import argparse
import collections
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")) and ROOT != os.path.dirname(ROOT):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot  # noqa: E402

MASK = (1 << 63) - 1
START, STOP = "\x02", "\x03"


def present(game, pool):
    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        if snap.game == game:
            ids = {i & MASK for i, p in snap.records if snap.pool_name(p) == pool}
            break
    else:
        raise SystemExit("no snapshot for %s" % game)
    names = set()
    for path in glob.glob(os.path.join(snapshot.settings.tables_csv(), "*.csv")):
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                _, _, name = line.partition(",")
                name = name.strip().lower().replace(chr(92), "/")
                if name:
                    names.add(name)
    names.update(n.strip().lower().replace(chr(92), "/") for n in snapshot.confirmed_names())
    return {n for n in names if snapshot.fnv1a(n) & MASK in ids}, ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--budget", type=int, default=5000000, help="stop after this many new candidates")
    ap.add_argument("--max-tokens", type=int, default=14)
    ap.add_argument("--min-count", type=int, default=2, help="drop transitions seen fewer times")
    ap.add_argument("--start", type=float, default=8.0, help="first threshold, in nats")
    ap.add_argument("--step", type=float, default=1.0)
    ap.add_argument("--holdout", type=float, default=0.0,
                    help="measure only: train without this share of known names, report how many come back")
    ap.add_argument("--family", default="", help="train and walk only names with this prefix")
    args = ap.parse_args()

    known, _ = present(args.game, args.pool)
    if args.family:
        known = {n for n in known if n.startswith(args.family)}
    held = set()
    if args.holdout:
        import random
        random.seed(1)
        held = {n for n in known if random.random() < args.holdout}
        known -= held
    trans = collections.defaultdict(collections.Counter)
    for name in known:
        toks = [START, START] + name.split("_") + [STOP]
        for i in range(2, len(toks)):
            trans[(toks[i - 2], toks[i - 1])][toks[i]] += 1

    model = {}
    for ctx, nxt in trans.items():
        total = sum(nxt.values())
        kept = [(-math.log(c / total), t) for t, c in nxt.items() if c >= args.min_count]
        if kept:
            kept.sort()
            model[ctx] = kept
    print("%s %s: %d known names, %d contexts" % (args.game, args.pool, len(known), len(model)),
          file=sys.stderr)

    # Each widening emits only the paths whose cost falls in the new band (previous threshold,
    # threshold], so nothing is held in memory and nothing is printed twice: tokens never contain
    # `_`, so distinct token paths are distinct strings.
    emitted = set() if held else None
    count = 0
    out = sys.stdout
    low, threshold = -1.0, args.start
    while count < args.budget and threshold < 80:
        stack = [((START, START), [], 0.0)]
        while stack and count < args.budget:
            ctx, toks, cost = stack.pop()
            for c, t in model.get(ctx, ()):
                total = cost + c
                if total > threshold:
                    break
                if t == STOP:
                    if toks and total > low:
                        name = "_".join(toks)
                        if name not in known:
                            count += 1
                            if held:
                                emitted.add(name)
                            else:
                                out.write(name + "\n")
                    continue
                if len(toks) < args.max_tokens:
                    stack.append(((ctx[1], t), toks + [t], total))
        print("  threshold %.1f: %d new candidates" % (threshold, count), file=sys.stderr)
        low, threshold = threshold, threshold + args.step
    if held:
        back = len(held & emitted)
        print("holdout: %d of %d held-out names regenerated (%.2f%%), 1 per %d candidates"
              % (back, len(held), 100.0 * back / len(held), count // max(1, back)), file=sys.stderr)


if __name__ == "__main__":
    main()
