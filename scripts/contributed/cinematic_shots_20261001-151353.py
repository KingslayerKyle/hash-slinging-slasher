r"""Cinematic shot animations, completed as the numeric grid they are.

`open_slot_alnum.py` found 133 Black Ops 4 anims on 2026-10-01, nearly all of one shape:
`ch_zm_mansion_outro_sh620_scarlett`, `o_zm_escape_outro_sh385_device` -- a scene, a shot number,
and the character or object animated in it. Shot numbers are an editor's grid (sh010, sh020, ...,
with sh005 or sh385 squeezed between), so they need no vocabulary: they can be enumerated.

For every scene prefix that carries `_sh<digits>_` in a known anim name, this offers

    - every shot sh000..sh995 in steps of 5, and a/b/c variants of the shots the scene is known to use
    - x every character or object (the part after the shot) seen in that scene *or in any sibling
      scene of the same map* -- the prefix minus its last token, so `..._outro` borrows from
      `..._intro` and `..._igc`

and also each scene's known shots under every scene prefix of its map (a shot list is often reused).

    python contrib/cinematic_shots.py --game BLKOPS04 | bin\windows\confirm_list.exe - \
        --game BLKOPS04 --label "cinematic shot grid" --script contrib/cinematic_shots.py
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

SHOT = re.compile(r"^(.+?)_(sh\d{2,4}[a-z]?)_(.+)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--pools", default="xanim,xmodel")
    args = ap.parse_args()

    out = sys.stdout
    total = 0
    for pool in args.pools.split(","):
        names, _ = token_markov.present(args.game, pool)
        shots = collections.defaultdict(set)
        rests = collections.defaultdict(set)
        for name in names:
            m = SHOT.match(name)
            if m:
                shots[m.group(1)].add(m.group(2))
                rests[m.group(1)].add(m.group(3))
        family = collections.defaultdict(set)
        for scene in shots:
            family[scene.rsplit("_", 1)[0]].add(scene)
        grid = ["sh%03d" % n for n in range(0, 1000, 5)]
        cands = set()
        for scene in shots:
            siblings = family[scene.rsplit("_", 1)[0]]
            who = set().union(*(rests[s] for s in siblings))
            numbers = set(grid)
            for s in shots[scene]:
                base = s.rstrip("abcdefgh")
                numbers |= {base + x for x in "abc"}
            for s in siblings:
                numbers |= shots[s]
            for n in numbers:
                for r in who:
                    cands.add(scene + "_" + n + "_" + r)
        cands -= names
        total += len(cands)
        out.write("".join(c + "\n" for c in sorted(cands)))
    print("%s: %d candidates" % (args.game, total), file=sys.stderr)


if __name__ == "__main__":
    main()
