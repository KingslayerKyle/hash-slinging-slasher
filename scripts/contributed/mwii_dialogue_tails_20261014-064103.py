"""Dialogue sound files for MWII: every known spoken-line stem under MWII's own tail grammar.

MWII had 19 named `.english` sound files on 2026-10-14 against MWIII's 62,783, though both ship the
iw9 operator battle chatter. The stem-x-target-tail transfer (sound_stem_tails.py) never tried a
language tail in MWII because MWII's measured tails held no `.english` one often enough to be kept.
Measured on 45,515 stems both games name: MWII drops the middle letter of MWIII's 3-letter format
code (`lnn`->`ln`, `snl`->`sl`, `lnl`->`ll`) and also uses 32000 Hz. So every dialogue stem known
in any modern game (language-tailed files, dotted) is crossed with format {sn,sc,sl,ln,pn,ss,cn},
quality {20,75,85}, rate {48000,32000,24000,44100} and language {english, english_safe}.

    python contrib/mwii_dialogue_tails.py | confirm_list - --game MODWAR22
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
if not (ROOT / "scripts" / "snapshot.py").is_file():
    raise SystemExit("Run this helper from within a hash-slinging-slasher checkout")
# Prepare these verified, game-and-pool-specific inputs with scripts/export_named.py.
if not (ROOT / "state" / "an").is_dir():
    raise SystemExit("Run python scripts/export_named.py first (see --help)")
stems = set()
for f in (ROOT / "state" / "an").glob("*_sound_asset.named"):
    for line in open(f, encoding="utf-8"):
        n = line.strip()
        if not n.endswith(("english", "english_safe")):
            continue
        if "/" in n:
            head, _, file = n.rpartition("/")
            n = head.replace("/", ".") + "." + file
        p = n.split(".")
        if len(p) >= 6:
            stems.add(".".join(p[:-4]))
fmts = ["sn", "sc", "sl", "ln", "pn", "ss", "cn"]
tails = [f"{f}.{q}.{r}.{l}" for f in fmts for q in (20, 75, 85) for r in (48000, 32000, 24000, 44100)
         for l in ("english", "english_safe")]
out = sys.stdout
for s in sorted(stems):
    for t in tails:
        out.write(s + "." + t + "\n")
print(f"{len(stems)} stems x {len(tails)} tails", file=sys.stderr)
