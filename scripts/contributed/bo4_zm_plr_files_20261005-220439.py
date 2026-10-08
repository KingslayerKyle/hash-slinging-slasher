r"""Black Ops 4 zombies player lines: every alias placed into every map's voice folder.

Measured 2026-10-05: 15,792 of Black Ops 4's 24,835 known `vox_` aliases have no known sound file,
and 14,535 of them have the zombies player-line shape `vox_<event>_plr_<n>_<idx>`
(`vox_scepter_ready_plr_12_0`). The few whose files are known show the rule -- the map code moves to
the front and the event behind the player number, and a take is appended:

    vox_scepter_ready_plr_12_0  ->  en\vox\scripted\zmb\man\vox_man_plr_12_scepter_ready_0_0.sn100.pc.snd

The only unknown is the map, and there are a dozen. So every such alias is offered under every
(map folder, map code) pair seen in a known zombies voice file, with takes 0..--takes.

    python contrib/bo4_zm_plr_files.py | bin\windows\confirm_list.exe - --game BLKOPS04 --no-fold ...
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402
from sound_word_slots import present_unfolded  # noqa: E402

ALIAS = re.compile(r"^vox_(.+)_plr_(\d+)_(\d+)$")
FOLDER = re.compile(r"^(en/vox/scripted/zmb/[a-z0-9_]+)/vox_([a-z0-9]+)_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--takes", type=int, default=4)
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    files = present_unfolded("BLKOPS04", "sound_asset")
    aliases, _ = token_markov.present("BLKOPS04", "sound_alias")
    maps = set()
    for f in files:
        m = FOLDER.match(f)
        if m:
            maps.add(m.groups())
    out = []
    for a in aliases:
        m = ALIAS.match(a)
        if not m:
            continue
        event, n, idx = m.groups()
        for folder, code in maps:
            # most lines: the alias's index is the file's take (`..._box_smg_3.sn100.pc.snd`), with an
            # occasional `_s` variant; map-specific lines add a separate take (`..._ready_0_0`)
            stem = "%s/vox_%s_plr_%s_%s_%s" % (folder, code, n, event, idx)
            forms = [stem, stem + "_s"] + ["%s_%d" % (stem, t) for t in range(args.takes)]
            out.extend(f + ".sn100.pc.snd" for f in forms if f + ".sn100.pc.snd" not in files)
    print("%d maps %s, %d candidates" % (len(maps), sorted(maps), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join(o.replace("/", chr(92)) + "\n" for o in out))


if __name__ == "__main__":
    main()
