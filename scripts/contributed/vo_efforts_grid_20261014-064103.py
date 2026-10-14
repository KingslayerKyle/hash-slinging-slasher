"""NPC/character effort voice files as a grid: every voice x every effort event x take x tail.

`vo_efforts/<voice>/dx_bc_effort_<event>_<NN>.<tail>` and
`vo_efforts/<voice>/<male|female>_npc_<voice>_<event>_<NN>.<tail>` (MWII/MWIII spell the `/` as `.`).
A voice is recorded against the same effort script as the others, so an event seen for one voice
is a candidate for every voice. Events, voices and take formats are read off every named modern
sound file; tails are the target game's own, measured on its vo_efforts files.
Found by the two-number grid on 2026-10-14 (MWII `male_npc_<v>_pain_<n>` families).

    python contrib/vo_efforts_grid.py MODWAR22 | confirm_list - --game MODWAR22
"""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run this helper from within a hash-slinging-slasher checkout")
# Prepare these verified, game-and-pool-specific inputs with scripts/export_named.py.
if not (ROOT / "state" / "an").is_dir():
    raise SystemExit("Run python scripts/export_named.py first (see --help)")
target = sys.argv[1].upper()
DOT = target in ("YAMYAMOK", "MODWAR22")
TAKE = re.compile(r"^(.*?)(_+)(alt)?(\d{1,3})$")

voices, bc_events, npc_events, takes = set(), collections.Counter(), collections.Counter(), collections.Counter()
tails = collections.Counter()
for f in (ROOT / "state" / "an").glob("*_sound_asset.named"):
    mine = f.name.startswith(target + "_")
    for line in open(f, encoding="utf-8"):
        n = line.strip()
        if not n.startswith("vo_efforts"):
            continue
        if "/" in n:
            parts = n.split("/")
            if len(parts) != 3:
                continue
            voice, file = parts[1], parts[2]
            stem, _, tail = file.partition(".")
        else:
            parts = n.split(".")
            if len(parts) != 7:
                continue
            voice, stem, tail = parts[1], parts[2], ".".join(parts[3:])
        if mine:
            tails[tail] += 1
        m = TAKE.match(stem)
        if not m:
            continue
        body, sep, alt, num = m.groups()
        takes[(sep, alt or "", len(num) if num.startswith("0") else 0)] += 1
        voices.add(voice)
        if body.startswith("dx_bc_effort_"):
            bc_events[body[len("dx_bc_effort_"):]] += 1
        else:
            mm = re.match(r"^(male|female)_npc_" + re.escape(voice) + r"_(.+)$", body)
            if mm:
                npc_events[mm.group(2)] += 1

tails = [t for t, c in tails.most_common() if c >= 5]
fmts = [k for k, c in takes.most_common() if c >= 20]
bodies = ["dx_bc_effort_" + e for e, c in bc_events.items() if c >= 2]
out = sys.stdout
count = 0
for v in sorted(voices):
    vb = bodies + [f"{g}_npc_{v}_{e}" for g in ("male", "female") for e, c in npc_events.items() if c >= 2]
    for b in vb:
        for sep, alt, width in fmts:
            for i in range(0, 31):
                s = str(i).zfill(width) if width else str(i)
                stem = f"{b}{sep}{alt}{s}"
                for t in tails:
                    out.write(f"vo_efforts.{v}.{stem}.{t}\n" if DOT else f"vo_efforts/{v}/{stem}.{t}\n")
                    count += 1
print(f"{len(voices)} voices, {len(bodies)} bc events, {len(npc_events)} npc events, {len(fmts)} take formats, {len(tails)} tails -> {count}", file=sys.stderr)
