"""Take numbers for one game's named sound files: every digit run in the stem, 0..max(40, top+20).

number_family_extend.py reads every name from every game and skips families with one member, so
a family that only just appeared in one game (MWII's 44100 Hz files, first named 2026-10-14) is
not extended. This works on one game's named sound files (state/an/<GAME>_sound_asset.named), keeps
the tail as it is, and fills every digit run of the stem at its width, including single members.

    python contrib/sound_take_fill.py MODWAR22 | confirm_list - --game MODWAR22
"""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
g = sys.argv[1].upper()
DIG = re.compile(r"\d+")
known = set(l.strip() for l in open(ROOT / "state" / "an" / f"{g}_sound_asset.named", encoding="utf-8") if l.strip())
fam = collections.defaultdict(set)
for n in known:
    p = n.split(".")
    if len(p) < 5:
        continue
    head = ".".join(p[:-4])
    tail = "." + ".".join(p[-4:])
    cut = head.rfind("/") + 1 if "/" in head else head.rfind(".") + 1
    for m in DIG.finditer(head):
        if m.start() < cut or len(m.group()) > 3:
            continue
        fam[(head[:m.start()], head[m.end():] + tail, len(m.group()) if m.group().startswith("0") else 0)].add(int(m.group()))
total = 0
for (pre, post, w), seen in fam.items():
    top = max(max(seen) + 20, 40)
    if w:
        top = min(top, 10 ** w - 1)
    for i in range(0, top + 1):
        if i in seen:
            continue
        sys.stdout.write(f"{pre}{str(i).zfill(w) if w else i}{post}\n")
        total += 1
print(f"{len(fam)} families -> {total}", file=sys.stderr)
