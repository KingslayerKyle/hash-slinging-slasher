"""BO6/BO7 `sgon_*` emissive images: every known prefix x every known `_gl_<hex>` chunk x tail.

`sgon_saw_sierra_farm_district_06_gl_c8a9cbee_2_emissivitymap`: the 8-hex chunk is shared between
unrelated prefixes (c8a9cbee in farm_district_06 and hospital_district_01; 7da918d6 in 66 of 471),
so a prefix seen with one chunk is a candidate with every other.

    python contrib/sgon_grid.py | confirm_list - --game BLACKOP7
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
PAT = re.compile(r"^(sgon_.+?)_gl_([0-9a-f]{8})_(\d+)_(.*)$")
names = set()
for f in [ROOT / "cod-name-db" / "csv" / "fnv1a_ximages_v2.csv"] + \
        [f for top in ("all_names", "findings") for f in (ROOT / top).rglob("image*.txt")]:
    for line in f.open(encoding="utf-8", errors="replace"):
        n = line.rstrip("\r\n").partition(",")[2].lower()
        if n.startswith("sgon_"):
            names.add(n)
pre, hx, tails = set(), set(), set()
for n in names:
    m = PAT.match(n)
    if m:
        pre.add(m[1]); hx.add(m[2]); tails.add("_" + m[3] + "_" + m[4])
for p in sorted(pre):
    for h in sorted(hx):
        for t in sorted(tails):
            print(f"{p}_gl_{h}{t}")
