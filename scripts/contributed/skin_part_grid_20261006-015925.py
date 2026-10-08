r"""Character skins x every body-part model form their faction uses (Cold War `c_t9_*`, BO4 `c_t8_*`).

A skin is `c_t9_<faction>_pl_<operator>_<skin>`; its models add a part and optional view/platform
endings (`_viewarms`, `_lowerbody_viewbody`, `_torso`, `_head`, `..._sy`). A skin known with only some
parts is a grid hole. Every skin key is offered every part ending seen on any skin of its faction.

    python contrib/skin_part_grid.py BLKOPSCW | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

PARTS = ("viewarms", "arms", "torso", "lowerbody", "head", "viewlegs", "legs", "body", "fullbody", "hands")


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "BLKOPSCW"
    tag = "c_t9_" if game == "BLKOPSCW" else "c_t8_"
    models, _ = token_markov.present(game, "xmodel")
    skins = collections.defaultdict(set)
    endings = collections.defaultdict(set)
    for m in models:
        if not m.startswith(tag):
            continue
        t = m.split("_")
        for i in range(len(t) - 1, 3, -1):
            if t[i] in PARTS:
                key, end = "_".join(t[:i]), "_".join(t[i:])
                faction = t[2]
                skins[faction].add(key)
                endings[faction].add(end)
                break
    out = set()
    for faction in skins:
        for key in skins[faction]:
            for end in endings[faction]:
                out.add(key + "_" + end)
    out -= models
    print("%d candidates" % len(out), file=sys.stderr)
    sys.stdout.write("".join(o + "\n" for o in out))


if __name__ == "__main__":
    main()
