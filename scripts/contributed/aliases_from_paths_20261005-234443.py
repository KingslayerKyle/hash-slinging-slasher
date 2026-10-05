r"""Sound aliases built from a sound file's *path*: top folder + chosen folder words + basename.

`aliases_from_files.py` only reads a file's basename. Cold War's effect aliases are usually built
from the path around it -- read off pairs on 2026-10-05:

    fly/weapon/reload/sniper_quick/bullet_in/sniper_quick_bullet_in_00   ->  fly_sniper_quick_bullet_in
    zmb/level/zm_silver/quest/ww/electric/crystal_empty/crystal_empty_00 ->  zmb_ww_crystal_empty
    wpn/.../plr/wpn_smg_cqb_loop                                         ->  wpn_smg_cqb_loop_plr

So every known sound file offers: its top folder + any ordered choice of up to --depth of its
intermediate folder names (split on `_`) + its basename minus the take, each with no suffix and with
`_plr` / `_npc`, and with a basename that already starts with the top folder not doubled.

    python contrib/aliases_from_paths.py --game BLKOPSCW | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import itertools
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from sound_word_slots import present_unfolded  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", required=True)
    ap.add_argument("--depth", type=int, default=2)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    files = present_unfolded(args.game, "sound_asset") if args.game == "BLKOPS04" else \
        token_markov.present(args.game, "sound_asset")[0]
    aliases, _ = token_markov.present(args.game, "sound_alias")
    out = set()
    for f in files:
        parts = f.split("/")
        if len(parts) < 2:
            continue
        top, middle, base = parts[0], parts[1:-1], parts[-1].split(".", 1)[0]
        base = re.sub(r"_\d+$", "", base)
        bases = {base}
        if base.startswith(top + "_"):
            bases.add(base[len(top) + 1:])
        mids = [m for m in middle if m and not m.isdigit() and m != "plr" and m != "npc"]
        for k in range(args.depth + 1):
            for combo in itertools.combinations(mids, k):
                for b in bases:
                    stem = "_".join([top] + list(combo) + [b])
                    for sfx in ("", "_plr", "_npc"):
                        out.add(stem + sfx)
    out -= aliases
    print("%s: %d files, %d candidates" % (args.game, len(files), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join(o + "\n" for o in out))


if __name__ == "__main__":
    main()
