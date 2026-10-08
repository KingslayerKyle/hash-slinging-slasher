r"""Images for every material, at every prefix of its name, with every measured channel ending.

Cold War's vehicle family has 11,674 materials and 5,336 images: materials stack paint and wear
variants (`..._exterior_c_carpaint_b_mpx_bp_bomber`, `..._rear_hull_mpx_dark_aether_glow`) on a part
whose images carry their own channel endings (`i_mtl_veh_t9_mil_ru_air_attack_frogfoot_canopy_maps1_r`,
`..._canopy_dead_maps2_r`, `..._canopy_o`). The image is named for the *part*, which is some prefix
of the material, not the whole material.

So every material, reduced to each of its prefixes of >= --min-tokens tokens, is offered as
`i_mtl_<prefix>_<ending>` and `i_<prefix>_<ending>` for the --endings commonest image endings
(the last one to three tokens of known image names, measured per game).

    python contrib/material_prefix_images.py --game BLKOPSCW | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--endings", type=int, default=60)
    ap.add_argument("--min-tokens", type=int, default=4)
    ap.add_argument("--per-family", type=int, default=0,
                    help="instead: endings measured inside each family (first 3 tokens of the part), top N each")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    images, _ = token_markov.present(args.game, "image")
    materials, _ = token_markov.present(args.game, "material")
    ends = collections.Counter()
    for i in images:
        t = i.split("_")
        for k in (1, 2, 3):
            if len(t) > k + 3:
                ends["_".join(t[-k:])] += 1
    endings = [e for e, _ in ends.most_common(args.endings)]
    prefixes = set()
    for m in materials:
        core = re.sub(r"^[a-z]+/", "", m)
        core = re.sub(r"^mtl_", "", core)
        t = core.split("_")
        for k in range(args.min_tokens, len(t) + 1):
            prefixes.add("_".join(t[:k]))
    out = sys.stdout
    total = 0
    if args.per_family:
        fam_ends = collections.defaultdict(collections.Counter)
        for i in images:
            core = re.sub(r"^i_(mtl_)?", "", i)
            t = core.split("_")
            fam = "_".join(t[:3])
            for k in (1, 2, 3):
                if len(t) > k + 3:
                    fam_ends[fam]["_".join(t[-k:])] += 1
        for p in prefixes:
            fam = "_".join(p.split("_")[:3])
            block = []
            for e, _ in fam_ends.get(fam, collections.Counter()).most_common(args.per_family):
                for head in ("i_mtl_", "i_"):
                    name = head + p + "_" + e
                    if name not in images:
                        block.append(name)
            total += len(block)
            if not args.count:
                out.write("".join(b + "\n" for b in block))
        print("%s: %d prefixes, per-family endings, %d candidates" % (args.game, len(prefixes), total),
              file=sys.stderr)
        return
    for p in prefixes:
        block = []
        for e in endings:
            for head in ("i_mtl_", "i_"):
                name = head + p + "_" + e
                if name not in images:
                    block.append(name)
        total += len(block)
        if not args.count:
            out.write("".join(b + "\n" for b in block))
    print("%s: %d prefixes x %d endings, %d candidates" % (args.game, len(prefixes), len(endings), total),
          file=sys.stderr)


if __name__ == "__main__":
    main()
