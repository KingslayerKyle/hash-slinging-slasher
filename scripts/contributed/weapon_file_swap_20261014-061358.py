"""Weapon sound files with the weapon swapped in the directory AND the file name at once.

`sat/wpn/ar/albatross/reloads/fly_plr_ar_albatross_inspect_empty_ext02_end.tnn.75.48000.all` names
its weapon twice, and t10/jup files also carry the weapon's rig code (`foly_plr_p14_pi_mable_...`,
`p08_ar_qbravo95_...`). weapon_slot_plan.py swaps `<class>_<weapon>` inside a name, so it keeps the
directory and never produces a coupled pair; this does: every named weapon file, every other
weapon of the same family and class, the weapon token replaced wherever it stands as a token and
the rig code replaced by the target weapon's own (the commonest `pNN` measured on its files).

Families: `<fam>/wpn/<class>/<weapon>/...` (sat, t10, jup, s6, ...) and `iw9/wpn/<class>_<weapon>/...`.
Reads state/an/*_sound_asset.named (contrib/_dump_named.py); dotted MWII/MWIII names are read
back to `/` and the output is printed in the requested spelling.

    python contrib/weapon_file_swap.py slash | confirm_list - --game BLACKOP7
    python contrib/weapon_file_swap.py dot   | confirm_list - --game YAMYAMOK
"""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
SPELL = sys.argv[1] if len(sys.argv) > 1 else "slash"
CODE = re.compile(r"(?:^|_)(p\d{1,3})_")


def to_slash(n):
    if "/" in n:
        return n
    parts = n.split(".")
    if len(parts) < 6:
        return None
    return "/".join(parts[:-4]) + "." + ".".join(parts[-4:])


def to_dot(n):
    head, _, file = n.rpartition("/")
    return head.replace("/", ".") + "." + file


files = set()
for f in (ROOT / "state" / "an").glob("*_sound_asset.named"):
    for line in f.open(encoding="utf-8", errors="replace"):
        n = to_slash(line.strip().lower())
        if n and "/wpn/" in n:
            files.add(n)

# (family, class) -> weapon -> [files]
groups = collections.defaultdict(lambda: collections.defaultdict(list))
for n in files:
    p = n.split("/")
    if len(p) < 4 or p[1] != "wpn":
        continue
    if p[0] == "iw9" or "_" in p[2]:
        if "_" not in p[2]:
            continue
        cls, _, w = p[2].partition("_")
    else:
        if len(p) < 5:
            continue
        cls, w = p[2], p[3]
    if w.startswith("_") or w in ("atmo", "shared"):
        continue
    groups[(p[0], cls)][w].append(n)

codes = {}
for key, weapons in groups.items():
    for w, fs in weapons.items():
        c = collections.Counter()
        for n in fs:
            stem = n.rsplit("/", 1)[1]
            if w in stem:
                c.update(CODE.findall(stem))
        if c:
            codes[(key, w)] = c.most_common(1)[0][0]


def swap(n, w, w2, c, c2):
    out = re.sub(r"(?<=[/_.])" + re.escape(w) + r"(?=[/_.])", w2, n)
    if c and c2 and c != c2:
        out = re.sub(r"(?<=[/_])" + c + r"(?=_)", c2, out)
    return out


seen = set()
count = 0
for key, weapons in groups.items():
    names = list(weapons)
    for w, fs in weapons.items():
        c = codes.get((key, w))
        for w2 in names:
            if w2 == w:
                continue
            c2 = codes.get((key, w2))
            for n in fs:
                out = swap(n, w, w2, c, c2)
                if out != n and out not in files and out not in seen:
                    seen.add(out)
                    print(to_dot(out) if SPELL == "dot" else out)
                    count += 1
print(f"{len(files)} weapon files, {sum(len(v) for v in groups.values())} weapons in {len(groups)} groups -> {count}", file=sys.stderr)
