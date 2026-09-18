"""Sound files: numbered takes well past the highest one known, and takes on stems that have none.

Every other sound derivation here widens a take family to max+2 or so. Recording sessions do not
stop where the corpus happens to have named up to, so this goes to max+12 (min 0..19), keeps the
family's own width, and also tries _00.._09 / _0.._9 on stems known only untaken.

    python contrib/sound_takes_wide.py --game BLKOPS04 | bin/windows/confirm_list.exe - --game BLKOPS04 --no-fold
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = sys.argv[sys.argv.index("--game") + 1].upper() if "--game" in sys.argv else "BLKOPS04"
TAKE = re.compile(r"^(.*?)_(\d{1,3})(\.[^\\/]*)$")
PLAIN = re.compile(r"^(.*?[^\d])(\.[^\\/]*)$")


def names():
    paths = [os.path.join(ROOT, "all_names", GAME.lower(), "sound_asset.txt")]
    paths += glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "fnv1a_*xsounds.csv"))
    paths += glob.glob(os.path.join(ROOT, "submissions", "*%s*" % GAME, "sound_asset*.txt"))
    paths += glob.glob(os.path.join(ROOT, "findings", GAME.lower(), "sound_asset.txt"))
    out = set()
    for path in paths:
        with open(path, encoding="utf-8-sig", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    out.add((line.split(",", 1)[1] if "," in line else line).lower().replace("/", "\\"))
    return out


def main():
    fam = collections.defaultdict(lambda: [-1, 2])
    plain = set()
    for n in names():
        head, _, base = n.rpartition("\\")
        m = TAKE.match(base)
        if m:
            f = fam[(head, m.group(1), m.group(3))]
            f[0] = max(f[0], int(m.group(2)))
            f[1] = len(m.group(2))
            continue
        m = PLAIN.match(base)
        if m:
            plain.add((head, m.group(1), m.group(2)))
    total = 0
    w = sys.stdout.write
    for (head, stem, sfx), (top, width) in fam.items():
        for i in range(max(top + 13, 20)):
            w("%s\\%s_%0*d%s\n" % (head, stem, width, i, sfx))
            total += 1
    for head, stem, sfx in plain:
        for i in range(10):
            w("%s\\%s_%02d%s\n%s\\%s_%d%s\n" % (head, stem, i, sfx, head, stem, i, sfx))
            total += 2
    print("takes wide %s: %d families, %d untaken, %d candidates" % (GAME, len(fam), len(plain), total),
          file=sys.stderr)


if __name__ == "__main__":
    main()
