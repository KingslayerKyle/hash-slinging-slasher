r"""Open word slots filled with new compounds of the words they already glue together.

Measured 2026-10-01: of the fillers in open word slots (frames with >= 4 alphabetic fillers), a
quarter are two English words joined with no separator -- 1,714 of 6,865 in Cold War, 1,433 of 6,408
in Black Ops 4: `licenseplate`, `wirefence`, `gunboat`, `bonusroom`, `matchstart`, `quickscope`.
A compound nobody has seen is a token no dictionary lists and no recombination of whole tokens can
make. But its *halves* are ordinary words, and a slot that glues `bonus|room` and `panic|room` is
likely to glue `safe|room` too.

For every open frame (exact prefix and suffix, >= --min fillers), each filler is split into two
words of wordfreq's top 50k where it can be. The frame's left halves L and right halves R (plain
fillers count as both) are then offered

    - L x R, crossed inside the frame
    - L x the top --top words, and the top --top words x R

each glued with no separator, and as its own exact frame.

    python contrib/compound_slots.py --game BLKOPSCW | bin\windows\confirm_list.exe - \
        --game BLKOPSCW --label "compound word slots" --script contrib/compound_slots.py
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
ALPHA = re.compile(r"^[a-z]{3,}$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--top", type=int, default=5000)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    from wordfreq import top_n_list
    english = {w for w in top_n_list("en", 50000) if ALPHA.match(w)}
    top = [w for w in top_n_list("en", args.top * 2) if ALPHA.match(w)][: args.top]

    def split2(w):
        for i in range(3, len(w) - 2):
            if w[:i] in english and w[i:] in english:
                return w[:i], w[i:]
        return None

    frames = collections.defaultdict(set)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        for name in names:
            toks = name.split("_")
            for i, tok in enumerate(toks):
                if ALPHA.match(tok):
                    head = "_".join(toks[:i]) + "_" if i else ""
                    tail = "_" + "_".join(toks[i + 1:]) if i < len(toks) - 1 else ""
                    frames[(head, tail)].add(tok)

    jobs = []
    total = 0
    for key, fillers in frames.items():
        if len(fillers) < args.min:
            continue
        left, right, glued = set(), set(), 0
        for f in fillers:
            parts = split2(f) if f not in english else None
            if parts:
                left.add(parts[0])
                right.add(parts[1])
                glued += 1
            elif f in english:
                left.add(f)
                right.add(f)
        if not glued:
            continue  # this slot never glues words; leave it to open_slot_words.py
        jobs.append((key, sorted(left), sorted(right), fillers))
        total += len(left) * len(right) + (len(left) + len(right)) * len(top)
    print("%s: %d compound-bearing open frames, about %d candidates" % (args.game, len(jobs), total),
          file=sys.stderr)
    if args.count:
        return
    out = sys.stdout
    for (head, tail), left, right, seen in jobs:
        inner = {a + b for a in left for b in right} - seen
        out.write("".join(head + c + tail + "\n" for c in inner))
        for a in left:
            out.write("".join(head + a + w + tail + "\n" for w in top))
        for b in right:
            out.write("".join(head + w + b + tail + "\n" for w in top))


if __name__ == "__main__":
    main()
