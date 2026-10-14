"""Every named modern sound file in the other game family's separator, both directions.

MWII/MWIII hash sound files with `.` directory separators (`iw9.dst.x_03.ln.75.48000.all`),
BO6/BO7/MW7 with `/`. sound_dots_transfer.py only goes `/` -> `.`; this also takes every dotted
name back to `/` (the last four dot fields are the tail: format, quality, rate, language), so
MWII/MWIII finds reach BO6/BO7/MW7. Reads state/an/*_sound_asset.named (contrib/_dump_named.py).

    python contrib/sound_sep_both.py slash | confirm_list - --game BLACKOP7
    python contrib/sound_sep_both.py dot   | confirm_list - --game YAMYAMOK
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
want = sys.argv[1] if len(sys.argv) > 1 else "slash"
seen = set()
for f in (ROOT / "state" / "an").glob("*_sound_asset.named"):
    for line in f.open(encoding="utf-8", errors="replace"):
        n = line.strip().lower()
        if not n:
            continue
        if "/" in n:
            head, _, file = n.rpartition("/")
            dotted = head.replace("/", ".") + "." + file
            slashed = n
        else:
            parts = n.split(".")
            if len(parts) < 6:
                continue
            body = parts[:-4]
            tail = ".".join(parts[-4:])
            slashed = "/".join(body) + "." + tail
            dotted = n
        out = slashed if want == "slash" else dotted
        if out not in seen:
            seen.add(out)
            print(out)
