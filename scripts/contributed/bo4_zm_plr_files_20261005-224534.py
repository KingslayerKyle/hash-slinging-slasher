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
    ap.add_argument("--aliases", action="store_true",
                    help="instead: every known zombies player-line file read back as its alias")
    ap.add_argument("--grid", action="store_true",
                    help="instead: every event x every player x the event's index range, as aliases"
                         " (and, with --grid-files, as files in every map)")
    ap.add_argument("--grid-files", action="store_true")
    ap.add_argument("--npc", action="store_true",
                    help="also non-player lines, vox_<event>_<npc>_<idx> -> vox_<map>_<npc>_<event>_<idx>")
    ap.add_argument("--all-folders", action="store_true",
                    help="every voice folder (en/vox/scripted/...) whose >= 20 files share a vox_<code>_ start,"
                         " not only the zombies maps")
    ap.add_argument("--count", action="store_true")
    args = ap.parse_args()

    files = present_unfolded("BLKOPS04", "sound_asset")
    aliases, _ = token_markov.present("BLKOPS04", "sound_alias")
    maps = set()
    for f in files:
        m = FOLDER.match(f)
        if m:
            maps.add(m.groups())
    if args.all_folders:
        import collections
        pairs = collections.Counter()
        for f in files:
            m = re.match(r"^(en/vox/scripted/.+)/vox_([a-z0-9]+)_", f)
            if m:
                pairs[m.groups()] += 1
        maps |= {k for k, v in pairs.items() if v >= 20}
    if args.aliases or args.grid:
        line = re.compile(r"^en/vox/scripted/zmb/[a-z0-9_]+/vox_[a-z0-9]+_plr_(\d+)_(.+)_(\d+)(?:_s)?\.sn100\.pc\.snd$")
        events = {}
        players = set()
        for f in files:
            m = line.match(f)
            if m:
                n, ev, idx = m.groups()
                players.add(n)
                events.setdefault(ev, set()).add(int(idx))
        for a in aliases:
            m = ALIAS.match(a)
            if m:
                ev, n, idx = m.groups()
                players.add(n)
                events.setdefault(ev, set()).add(int(idx))
        out = set()
        if args.aliases:
            for f in files:
                m = line.match(f)
                if m:
                    n, ev, idx = m.groups()
                    out.add("vox_%s_plr_%s_%s" % (ev, n, idx))
        if args.grid:
            for ev, idxs in events.items():
                for n in players:
                    for i in range(max(idxs) + 2):
                        out.add("vox_%s_plr_%s_%d" % (ev, n, i))
                        if args.grid_files:
                            for folder, code in maps:
                                out.add("%s/vox_%s_plr_%s_%s_%d.sn100.pc.snd" % (folder, code, n, ev, i))
        out = [o for o in out if o not in aliases and o not in files]
        print("%d events, %d players, %d candidates" % (len(events), len(players), len(out)), file=sys.stderr)
        if not args.count:
            sys.stdout.write("".join((o.replace("/", chr(92)) if "/" in o else o) + "\n" for o in out))
        return
    out = []
    npc = re.compile(r"^vox_(.+)_([a-z][a-z0-9]*)_(\d+)$")
    for a in aliases:
        m = ALIAS.match(a)
        who = None
        if m:
            event, n, idx = m.groups()
            who = "plr_" + n
        elif args.npc:
            m = npc.match(a)
            if m:
                event, who, idx = m.groups()
        if not who:
            continue
        for folder, code in maps:
            # most lines: the alias's index is the file's take (`..._box_smg_3.sn100.pc.snd`), with an
            # occasional `_s` variant; map-specific lines add a separate take (`..._ready_0_0`)
            stem = "%s/vox_%s_%s_%s_%s" % (folder, code, who, event, idx)
            forms = [stem, stem + "_s"] + ["%s_%d" % (stem, t) for t in range(args.takes)]
            out.extend(f + ".sn100.pc.snd" for f in forms if f + ".sn100.pc.snd" not in files)
    print("%d maps %s, %d candidates" % (len(maps), sorted(maps), len(out)), file=sys.stderr)
    if not args.count:
        sys.stdout.write("".join(o.replace("/", chr(92)) + "\n" for o in out))


if __name__ == "__main__":
    main()
