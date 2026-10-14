"""Two-number families filled as a grid: both digit slots varied together.

`jup_vinyl_b5027_5`, `compass_map_mp_saw_sierra_01_02`, `ui_emblem_set_12_03`: a name with two runs
of digits is a member of a 2-D family. number_family_extend.py varies one slot with the other held
at a value somebody has seen, so a member whose pair of numbers matches no known member in either
slot is never generated. Here each family (text around the two slots, both widths) gets the full
grid min..max (+ a margin) of each slot, minus what is known. Families with fewer than --min members
or a grid over --cap are skipped.

    python contrib/number_grid2.py --kind image | confirm_list - --game YAMYAMOK --script contrib/number_grid2.py
"""
from pathlib import Path
import argparse
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
ap = argparse.ArgumentParser()
ap.add_argument("--kind", default="image")
ap.add_argument("--min", type=int, default=4)
ap.add_argument("--cap", type=int, default=20000)
ap.add_argument("--margin", type=float, default=0.25)
ap.add_argument("--size", action="store_true")
a = ap.parse_args()

DIG = re.compile(r"\d+")
known = set()
for f in (ROOT / "state" / "an").glob(f"*_{a.kind}.named"):
    known.update(l.strip() for l in open(f, encoding="utf-8") if l.strip())

fam = collections.defaultdict(set)
for n in known:
    runs = list(DIG.finditer(n))
    if len(runs) < 2 or len(runs) > 4:
        continue
    for i in range(len(runs)):
        for j in range(i + 1, len(runs)):
            r1, r2 = runs[i], runs[j]
            key = (n[:r1.start()], n[r1.end():r2.start()], n[r2.end():],
                   len(r1.group()) if r1.group().startswith("0") and len(r1.group()) > 1 else 0,
                   len(r2.group()) if r2.group().startswith("0") and len(r2.group()) > 1 else 0)
            fam[key].add((int(r1.group()), int(r2.group())))

total = 0
out = sys.stdout
for (pre, mid, post, w1, w2), pts in fam.items():
    if len(pts) < a.min:
        continue
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    x1 += int((x1 - x0) * a.margin) + 1
    y1 += int((y1 - y0) * a.margin) + 1
    x0 = max(0, x0 - 1)
    y0 = max(0, y0 - 1)
    size = (x1 - x0 + 1) * (y1 - y0 + 1)
    if size > a.cap or size <= len(pts):
        continue
    total += size
    if a.size:
        continue
    for x in range(x0, x1 + 1):
        sx = str(x).zfill(w1) if w1 else str(x)
        for y in range(y0, y1 + 1):
            sy = str(y).zfill(w2) if w2 else str(y)
            out.write(f"{pre}{sx}{mid}{sy}{post}\n")
print(f"{len(fam)} families, total grid {total}", file=sys.stderr)
