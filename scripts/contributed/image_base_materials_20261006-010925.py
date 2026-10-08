r"""Materials for every image base, with every measured material ending.

The reverse of `material_prefix_images.py`. A material is a part (the image's base) plus variant
tokens -- paint, wear, skin (`..._rear_hull_mpx_dark_aether_glow`, `..._wheels_dead_low`) -- so every
known image, with its channel ending removed (the commonest 1-3 token image endings, measured per
game), is offered as `mc/mtl_<base>` and `mc/mtl_<base>_<ending>` for the --endings commonest
material endings.

    python contrib/image_base_materials.py --game BLKOPSCW | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402


def tail_counts(names, strip):
    ends = collections.Counter()
    for n in names:
        t = strip(n).split("_")
        for k in (1, 2, 3):
            if len(t) > k + 3:
                ends["_".join(t[-k:])] += 1
    return ends


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--channels", type=int, default=60)
    ap.add_argument("--endings", type=int, default=200)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    images, _ = token_markov.present(args.game, "image")
    materials, _ = token_markov.present(args.game, "material")
    channels = [e for e, _ in tail_counts(images, lambda n: n).most_common(args.channels)]
    mat_core = lambda m: re.sub(r"^mtl_", "", re.sub(r"^[a-z]+/", "", m))  # noqa: E731
    endings = [""] + ["_" + e for e, _ in tail_counts(materials, mat_core).most_common(args.endings)]
    bases = set()
    for i in images:
        core = re.sub(r"^i_(mtl_)?", "", i)
        for ch in channels:
            if core.endswith("_" + ch):
                bases.add(core[: -len(ch) - 1])
    out = sys.stdout
    total = 0
    for b in bases:
        block = ["mc/mtl_" + b + e for e in endings if "mc/mtl_" + b + e not in materials]
        total += len(block)
        if not args.count:
            out.write("".join(x + "\n" for x in block))
    print("%s: %d image bases x %d endings, %d candidates" % (args.game, len(bases), len(endings), total),
          file=sys.stderr)


if __name__ == "__main__":
    main()
