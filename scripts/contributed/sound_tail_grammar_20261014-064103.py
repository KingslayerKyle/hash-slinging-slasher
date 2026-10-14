"""Every known modern sound-file stem under the target game's whole tail GRAMMAR, not its top tails.

A tail is `<format>.<quality>.<rate>.<language>`. sound_stem_tails.py crosses stems with the tails a
game already shows 20+ times, so a (format, quality, rate) combination the game uses rarely -- or
has simply not had named yet -- is never tried. Here each field is crossed independently:
format codes measured on the target game (5+ uses; for MWII the 2-letter codes, which are MWIII's
3-letter codes minus the middle letter, measured on 45,515 shared stems), quality
{20,50,75,85,100}, rate {48000,32000,24000,44100}, language `all`. Stems come from every named
modern sound file (dialogue excluded), in the target's separator.
First run 2026-10-14: MWII 392 new.

    python contrib/sound_tail_grammar.py MODWAR22 | confirm_list - --game MODWAR22
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
target = sys.argv[1].upper()
DOT = target in ("YAMYAMOK", "MODWAR22")


def parts_of(n):
    if "/" in n:
        h, _, fl = n.rpartition("/")
        n = h.replace("/", ".") + "." + fl
    p = n.split(".")
    return p if len(p) >= 6 else None


stems = set()
fm = collections.Counter()
for f in (ROOT / "state" / "an").glob("*_sound_asset.named"):
    mine = f.name.startswith(target + "_")
    for line in open(f, encoding="utf-8"):
        n = line.strip()
        p = parts_of(n)
        if not p or not p[-1] == "all":
            continue
        stems.add(tuple(p[:-4]))
        c = p[-4]
        if target == "MODWAR22" and len(c) == 3:
            c = c[0] + c[2]
        if mine or target == "MODWAR22":
            fm[c] += 1
want_len = 2 if target == "MODWAR22" else 3
fmts = [c for c, k in fm.most_common() if k >= 5 and len(c) == want_len]
tails = [f"{f}.{q}.{r}.all" for f in fmts for q in (20, 50, 75, 85, 100) for r in (48000, 32000, 24000, 44100)]
out = sys.stdout
for s in stems:
    base = ".".join(s) if DOT else "/".join(s[:-1]) + "/" + s[-1]
    for t in tails:
        out.write(base + "." + t + "\n")
print(f"{target}: {len(stems)} stems x {len(tails)} tails ({fmts})", file=sys.stderr)
