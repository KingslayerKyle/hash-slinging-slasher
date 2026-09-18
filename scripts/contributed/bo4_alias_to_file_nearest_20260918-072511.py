"""BO4 sound files for known aliases, placed in the directory of their nearest named sibling.

A sound file's stem is usually its alias plus a take:  alias evt_ee_cage_lift  ->
    ...\\evt_ee_cage_lift_00.sn100.pc.snd
Method 153 did this for vox only, into a fixed en\\vox\\scripted\\<mode>\\<map> grid. For every
other family the directory is unknown -- but a sibling alias usually has a named file, and siblings
live together. So for each known alias with no named file:

  - find the named files whose stem (take removed) shares the longest token prefix with it
    (at least --min-prefix tokens), and take their directories and suffixes
  - emit dir\\<alias>[_take].<suffix>, takes 0..(sibling max+2) at the sibling's width, and untaken

    python contrib/bo4_alias_to_file_nearest.py | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_PREFIX = int(sys.argv[sys.argv.index("--min-prefix") + 1]) if "--min-prefix" in sys.argv else 2
TAKE = re.compile(r"^(.*?)(?:_(\d{1,3}))?$")


def rows(paths):
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    yield (line.split(",", 1)[1] if "," in line else line).strip().lower()


def main():
    files = glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_*xsounds.csv"))
    files += [os.path.join(ROOT, "all_names", "blkops04", "sound_asset.txt"),
              os.path.join(ROOT, "findings", "blkops04", "sound_asset.txt")]
    files += glob.glob(os.path.join(ROOT, "submissions", "*BLKOPS04*", "sound_asset*.txt"))
    aliases = [os.path.join(ROOT, "all_names", "blkops04", "sound_alias.txt"),
               os.path.join(ROOT, "findings", "blkops04", "sound_alias.txt")]
    aliases += glob.glob(os.path.join(ROOT, "submissions", "*BLKOPS04*", "sound_alias*.txt"))

    # token-prefix -> {(dir, suffix, width, top)}
    by_prefix = collections.defaultdict(set)
    have = set()
    for n in rows(files):
        n = n.replace("/", "\\")
        if "\\" not in n or "\\vox\\" in n:
            continue
        d, base = n.rsplit("\\", 1)
        dot = base.find(".")
        if dot <= 0:
            continue
        m = TAKE.match(base[:dot])
        stem, take = m.group(1), m.group(2)
        have.add(stem)
        toks = stem.split("_")
        width = len(take) if take else 0
        top = int(take) if take else -1
        for k in range(MIN_PREFIX, len(toks) + 1):
            by_prefix["_".join(toks[:k])].add((d, base[dot:], width, top))

    total = 0
    w = sys.stdout.write
    for a in set(rows(aliases)):
        if a in have or a.startswith("vox_"):
            continue
        toks = a.split("_")
        spots = None
        for k in range(len(toks), MIN_PREFIX - 1, -1):
            spots = by_prefix.get("_".join(toks[:k]))
            if spots:
                break
        if not spots:
            continue
        # collapse to dir/suffix with the widest take seen there
        best = {}
        for d, sfx, width, top in spots:
            key = (d, sfx)
            ow, ot = best.get(key, (0, -1))
            best[key] = (max(ow, width), max(ot, top))
        if len(best) > 40:
            continue
        for (d, sfx), (width, top) in best.items():
            w("%s\\%s%s\n" % (d, a, sfx))
            total += 1
            for i in range(max(top + 3, 4)):
                for wd in {width or 2, 1, 2}:
                    w("%s\\%s_%0*d%s\n" % (d, a, wd, i, sfx))
                    total += 1
    print("alias->file nearest: %d candidates" % total, file=sys.stderr)


if __name__ == "__main__":
    main()
