"""Every known modern sound file, re-spelled with `.` directory separators for MWII/MWIII.

MWII and MWIII hash sound files as `iw9.dst.iw9_dst_street_barricade_03.ln.75.48000.all`; BO6/BO7
hash the `/` spelling. Measured 2026-10-09 against the captures: xsounds_v2 names reproduce 174,233
MWIII ids dotted and 119 slashed; BO6 101,806 slashed and 1 dotted. So a name known from BO6/BO7
(or any `/` generator output) only reaches MWIII once re-spelled.

    python contrib/sound_dots_transfer.py | confirm_list - --game YAMYAMOK
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

seen = set()
out = sys.stdout
srcs = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_xsounds_v2*.csv"))
for top in ("all_names", "findings", "submissions"):
    srcs += [f for f in (ROOT / top).rglob("sound_asset*.txt")
             if any(g in str(f).lower() for g in ("blackop6", "blackop7", "modwar7", "yamyamok", "modwar22"))]
for f in srcs:
    for line in f.open(encoding="utf-8", errors="replace"):
        name = line.rstrip("\r\n").partition(",")[2].lower()
        if "/" in name:
            d = name.replace("/", ".")
            if d not in seen:
                seen.add(d)
                out.write(d + "\n")
