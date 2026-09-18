"""BO4 zombies player vox as a grid: map x player x line x take.

    en\\vox\\scripted\\zmb\\<map>\\vox_<abbr>_plr_<n>_<line>_<take>.sn100.pc.snd

~22.6k are named across white/bod/orange/red/tow/zod/man/fiv. Every map records the same generic
lines (powerup_*, box_*, *_kill, generic_responses_*) for each of its players, so:

  - within a map: every player x every line any player of that map has
  - --cross: also every line seen on any map (generic lines move between maps)
  - takes 0 .. max+2 of that line (on any map in --cross), at the width seen

    python contrib/bo4_zmb_vox_grid.py [--cross] | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RX = re.compile(r"^en\\vox\\scripted\\zmb\\([^\\]+)\\vox_([a-z0-9]+)_plr_(\d+)_(.+?)_(\d{1,3})(\.[a-z0-9.]+)$")


def names():
    paths = [os.path.join(ROOT, "all_names", "blkops04", "sound_asset.txt")]
    paths += glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_*xsounds.csv"))
    paths += glob.glob(os.path.join(ROOT, "submissions", "*BLKOPS04*", "sound_asset*.txt"))
    paths += glob.glob(os.path.join(ROOT, "findings", "blkops04", "sound_asset.txt"))
    for path in paths:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    yield (line.split(",", 1)[1] if "," in line else line).lower().replace("/", "\\")


def main():
    cross = "--cross" in sys.argv
    maps = collections.defaultdict(lambda: {"abbr": set(), "plr": set(), "lines": {}, "sfx": set()})
    glob_lines = {}
    for n in names():
        m = RX.match(n)
        if not m:
            continue
        mp, abbr, plr, line, take, sfx = m.groups()
        d = maps[mp]
        d["abbr"].add(abbr)
        d["plr"].add(plr)
        d["sfx"].add(sfx)
        t, w = int(take), len(take)
        d["lines"][line] = (max(d["lines"].get(line, (-1, w))[0], t), w)
        glob_lines[line] = (max(glob_lines.get(line, (-1, w))[0], t), w)
    total = 0
    w = sys.stdout.write
    for mp, d in maps.items():
        lines = dict(glob_lines) if cross else d["lines"]
        if cross:
            lines.update({k: (max(v[0], glob_lines[k][0]), v[1]) for k, v in d["lines"].items()})
        for abbr in d["abbr"]:
            for plr in d["plr"]:
                for line, (top, width) in lines.items():
                    for i in range(top + 3):
                        for sfx in d["sfx"]:
                            w("en\\vox\\scripted\\zmb\\%s\\vox_%s_plr_%s_%s_%0*d%s\n"
                              % (mp, abbr, plr, line, width, i, sfx))
                            total += 1
    print("zmb vox grid: %d maps, %d lines, %d candidates" % (len(maps), len(glob_lines), total),
          file=sys.stderr)


if __name__ == "__main__":
    main()
