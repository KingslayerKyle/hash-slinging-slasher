r"""Every numbered designation slot, enumerated over its whole range.

`cinematic_shots.py` turned one designation grid -- shot numbers, `sh010`..`sh995` -- into 117 Black
Ops 4 anims from 130k candidates on 2026-10-01, and `open_slot_alnum.py` had found 133 more just by
offering codes seen elsewhere. The general shape: a slot whose fillers are a fixed letter prefix plus
a fixed-width number (and sometimes a letter after it) is an editor's counter, and its missing cells
need no vocabulary.

For every exact frame (known prefix and suffix around one token), fillers of the form
`<letters><digits>[<letter>]` are grouped by (letters, digit width, trailing letter or not). A group
of >= --min fillers is enumerated:

    width 1-3   every number of that width
    width 4+    every number from (smallest - --pad) to (largest + --pad)
    trailing    each number with a, b, c, d when the group has trailing letters

Final slots included: closure's numbered variants step a known number, this fills a counter's range.

    python contrib/numeric_slots.py --game BLKOPS04 | bin\windows\confirm_list.exe - \
        --game BLKOPS04 --label "numbered designation slots" --script contrib/numeric_slots.py
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

POOLS = ("xmodel", "image", "material", "xanim", "sound_alias")
DESIG = re.compile(r"^([a-z]*)(\d+)([a-z]?)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--min", type=int, default=2)
    ap.add_argument("--pad", type=int, default=50)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    known = set()
    groups = collections.defaultdict(list)
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        known |= names
        for name in names:
            toks = name.split("_")
            for i, tok in enumerate(toks):
                m = DESIG.match(tok)
                if not m:
                    continue
                head = "_".join(toks[:i]) + "_" if i else ""
                tail = "_" + "_".join(toks[i + 1:]) if i < len(toks) - 1 else ""
                letters, digits, trail = m.groups()
                groups[(head, tail, letters, len(digits), bool(trail))].append(int(digits))
    out = sys.stdout
    total = 0
    for (head, tail, letters, width, trailing), nums in groups.items():
        if len(set(nums)) < args.min:
            continue
        if width <= 3:
            rng = range(0, 10 ** width)
        else:
            rng = range(max(0, min(nums) - args.pad), min(10 ** width, max(nums) + args.pad + 1))
        suffixes = ("a", "b", "c", "d") if trailing else ("",)
        block = []
        for n in rng:
            for sfx in suffixes:
                cand = "%s%s%0*d%s%s" % (head, letters, width, n, sfx, tail)
                if cand not in known:
                    block.append(cand)
        total += len(block)
        if not args.count:
            out.write("".join(c + "\n" for c in block))
    print("%s: %d candidates" % (args.game, total), file=sys.stderr)


if __name__ == "__main__":
    main()
