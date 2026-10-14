"""Every named modern sound-file stem under every tail the TARGET game uses, in its separator.

A sound file is `<dir>/<stem>.<fmt>.<quality>.<rate>.<language>`, and the format code differs by
game for the same source file: BO7 `iw9/wpn/.../x.tnn.85.48000.all`, MW7 `...x.lnn.85...` /
`vnn` / `qnn` / `hnn`. Names already move between games when the whole string matches (shared id
space); this moves the stem and re-dresses it in each of the target game's measured tails (all
tails seen 20+ times on its named files) and its separator (`.` for MWII/MWIII, `/` otherwise).

    python scripts/export_named.py BLACKOP6 BLACKOP7 YAMYAMOK MODWAR22 MODWAR7
    python contrib/sound_stem_tails.py MODWAR7 | confirm_list - --game MODWAR7
"""
from pathlib import Path
import collections
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run this helper from within a hash-slinging-slasher checkout")
# Prepare these verified, game-and-pool-specific inputs with scripts/export_named.py.
if not (ROOT / "state" / "an").is_dir():
    raise SystemExit("Run python scripts/export_named.py first (see --help)")
AN = ROOT / "state" / "an"
target = sys.argv[1].upper()
DOTTED = {"YAMYAMOK", "MODWAR22"}


def split(n):
    """(dir parts, stem, tail) from either spelling, or None."""
    if "/" in n:
        head, _, file = n.rpartition("/")
        parts = file.split(".")
        if len(parts) < 5:
            return None
        return head.split("/"), ".".join(parts[:-4]), ".".join(parts[-4:])
    parts = n.split(".")
    if len(parts) < 6:
        return None
    return parts[:-5], parts[-5], ".".join(parts[-4:])


tails = collections.Counter()
for line in open(AN / f"{target}_sound_asset.named", encoding="utf-8"):
    s = split(line.strip())
    if s:
        tails[s[2]] += 1
tails = [t for t, c in tails.most_common() if c >= 20]

seen = set()
for f in AN.glob("*_sound_asset.named"):
    for line in open(f, encoding="utf-8"):
        s = split(line.strip())
        if not s:
            continue
        key = (tuple(s[0]), s[1])
        if key in seen:
            continue
        seen.add(key)
        sep = "." if target in DOTTED else "/"
        base = sep.join(s[0]) + sep + s[1]
        for t in tails:
            print(base + "." + t)
print(f"{len(seen)} stems x {len(tails)} tails", file=sys.stderr)
