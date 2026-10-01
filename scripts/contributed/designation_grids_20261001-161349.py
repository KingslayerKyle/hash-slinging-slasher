r"""Numbered designations x the continuations their siblings use: `cinematic_shots.py`, generalised.

The shot grid paid because it crossed two axes at once -- every shot number, and every character or
object any shot of that scene animates. The same two axes exist wherever a name has a lettered
counter followed by something that varies: `..._sh385_device`, `..._s04_<prop>`, `..._v02_<variant>`.

For every prefix H and designation shape (letters L, digit width W <= 3) seen as `H_<L><digits>_<tail>`
in a known name of one pool, with >= --min distinct designations and >= 2 distinct tails, this offers
every number of width W (plus a/b/c variants of the known ones) x every tail seen after any
designation under H (capped at the --cap commonest). `--bare` also takes counters with no letters
(`_01_`), which are far more numerous.

    python contrib/designation_grids.py --game BLKOPS04 | bin\windows\confirm_list.exe - \
        --game BLKOPS04 --label "designation grids" --script contrib/designation_grids.py
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
    ap.add_argument("--min", type=int, default=3)
    ap.add_argument("--cap", type=int, default=300)
    ap.add_argument("--bare", action="store_true")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    out = sys.stdout
    total = 0
    for pool in POOLS:
        names, _ = token_markov.present(args.game, pool)
        desig = collections.defaultdict(set)
        tails = collections.defaultdict(collections.Counter)
        for name in names:
            toks = name.split("_")
            for i, tok in enumerate(toks[:-1]):
                m = DESIG.match(tok)
                if not m or (not m.group(1) and not args.bare) or len(m.group(2)) > 3:
                    continue
                key = ("_".join(toks[:i]), m.group(1), len(m.group(2)))
                desig[key].add(tok)
                tails[key]["_".join(toks[i + 1:])] += 1
        cands = set()
        for key, seen in desig.items():
            if len(seen) < args.min or len(tails[key]) < 2:
                continue
            head, letters, width = key
            numbers = {"%s%0*d" % (letters, width, n) for n in range(10 ** width)}
            for s in seen:
                base = s.rstrip("abcdefgh")
                numbers |= {base + x for x in "abc"}
            prefix = head + "_" if head else ""
            for t, _ in tails[key].most_common(args.cap):
                for n in numbers:
                    cands.add(prefix + n + "_" + t)
        cands -= names
        total += len(cands)
        if not args.count:
            out.write("".join(c + "\n" for c in sorted(cands)))
    print("%s: %d candidates" % (args.game, total), file=sys.stderr)


if __name__ == "__main__":
    main()
