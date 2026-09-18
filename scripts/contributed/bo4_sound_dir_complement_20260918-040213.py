"""BO4 sound files: give every sibling directory the files its siblings are known to have.

Generalises contrib/bo4_vox_slot_transfer.py (which paid 28 on vox speaker slots, 2026-09-17) to
every BO4 sound path. Under one parent, sibling directories are usually parallel sets -- one per
weapon, character, surface, map -- holding the same file stems. So for each parent:

  - a child's stem is normalised by replacing its own directory token (when the stem contains it)
    with a placeholder, e.g.  fly\\hub\\adler\\fly_adler_step_02  ->  fly_{}_step_02
  - every normalised stem seen under any child is emitted under every other child, with the
    placeholder filled back in
  - suffixes are the ones seen under that parent; numbered takes widened to max+2

Parents whose cross is larger than --cap candidates are skipped (and counted on stderr), which keeps
it to the families that are actually parallel rather than a directory of everything.

    python contrib/bo4_sound_dir_complement.py | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
    python contrib/bo4_sound_dir_complement.py --game BLKOPSCW | bin/windows/confirm_list.exe - --game BLKOPSCW
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS = "\\"
TAKE = re.compile(r"^(.*?)_(\d{1,3})$")


GAME = sys.argv[sys.argv.index("--game") + 1].upper() if "--game" in sys.argv else "BLKOPS04"


def known():
    names = set()
    paths = [os.path.join(ROOT, "all_names", GAME.lower(), "sound_asset.txt")]
    paths += glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_*xsounds.csv"))
    paths += glob.glob(os.path.join(ROOT, "submissions", "*%s*" % GAME, "sound_asset*.txt"))
    paths += glob.glob(os.path.join(ROOT, "findings", GAME.lower(), "sound_asset.txt"))
    for path in paths:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                name = line.split(",", 1)[1] if "," in line else line
                names.add(name.strip().lower().replace("/", BS))
    return names


def main():
    cap = 2_000_000
    if "--cap" in sys.argv:
        cap = int(sys.argv[sys.argv.index("--cap") + 1])
    # parent -> child -> set(normalised stem) ; parent -> suffixes ; (parent, stem) -> top take
    fam = collections.defaultdict(lambda: collections.defaultdict(set))
    sfx = collections.defaultdict(set)
    top = collections.defaultdict(lambda: -1)
    for name in known():
        parts = name.split(BS)
        if len(parts) < 3:
            continue
        parent, child, base = BS.join(parts[:-2]), parts[-2], parts[-1]
        dot = base.find(".")
        if dot <= 0:
            continue
        stem = base[:dot]
        sfx[parent].add(base[dot:])
        norm = stem.replace(child, "{}") if len(child) >= 3 else stem
        m = TAKE.match(norm)
        if m:
            key, n, width = m.group(1), int(m.group(2)), len(m.group(2))
            norm = "%s_#%d" % (key, width)
            top[(parent, norm)] = max(top[(parent, norm)], n)
        fam[parent][child].add(norm)

    total = skipped = used = 0
    out = sys.stdout
    for parent, children in fam.items():
        if len(children) < 2:
            continue
        union = set().union(*children.values())
        takes = 0
        for norm in union:
            takes += (top[(parent, norm)] + 3) if "#" in norm else 1
        size = len(children) * takes * len(sfx[parent])
        if size > cap:
            skipped += 1
            continue
        used += 1
        for child in children:
            for norm in union:
                if "#" in norm:
                    key, width = norm.rsplit("_#", 1)
                    width = int(width)
                    stems = ["%s_%0*d" % (key, width, i) for i in range(top[(parent, norm)] + 3)]
                else:
                    stems = [norm]
                for stem in stems:
                    stem = stem.replace("{}", child)
                    for s in sfx[parent]:
                        out.write("%s\\%s\\%s%s\n" % (parent, child, stem, s))
                        total += 1
    print("dir complement: %d parents used, %d over cap, %d candidates" % (used, skipped, total),
          file=sys.stderr)


if __name__ == "__main__":
    main()
