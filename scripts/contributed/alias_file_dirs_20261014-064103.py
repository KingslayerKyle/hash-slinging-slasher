"""Sound files from a game's named aliases, each placed in the directories its neighbours live in.

In MWII 8,910 of 48,700 named files (18%) are `<dir>.<alias>[_NN].<tail>` for a named alias. An
alias whose files are not named needs a directory: take the directories of named files whose stems
share the alias's first 3 (else 2) underscore tokens, at most --dirs of the commonest. Crossed with
takes (none, _01.._NN, _1.._N) and the game's commonest tails (incl. MWII's 44100 Hz ones).

    python contrib/alias_file_dirs.py MODWAR22 | confirm_list - --game MODWAR22
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
g = sys.argv[1].upper()
DOT = g in ("YAMYAMOK", "MODWAR22")
NDIRS = 6
TAKES = 20
NTAILS = 10

files = [l.strip() for l in open(AN / f"{g}_sound_asset.named", encoding="utf-8") if l.strip()]
aliases = set(l.strip() for l in open(AN / f"{g}_sound_alias.named", encoding="utf-8") if l.strip())
by_head = collections.defaultdict(collections.Counter)
tails = collections.Counter()
have = set()
for n in files:
    if DOT:
        p = n.split(".")
        if len(p) < 6:
            continue
        d, stem, tail = ".".join(p[:-5]), p[-5], ".".join(p[-4:])
    else:
        h, _, fl = n.rpartition("/")
        q = fl.split(".")
        if len(q) < 5:
            continue
        d, stem, tail = h, q[0], ".".join(q[1:])
    tails[tail] += 1
    have.add(stem)
    t = stem.split("_")
    for k in (2, 3):
        if len(t) > k:
            by_head["_".join(t[:k])][d] += 1
tails = [t for t, _ in tails.most_common(NTAILS)]
sep = "." if DOT else "/"
count = 0
for a in sorted(aliases):
    if a in have:
        continue
    t = a.split("_")
    dirs = by_head.get("_".join(t[:3])) or by_head.get("_".join(t[:2]))
    if not dirs:
        continue
    for d, _ in dirs.most_common(NDIRS):
        for take in [""] + [f"_{i:02d}" for i in range(1, TAKES + 1)] + [f"_{i}" for i in range(1, 10)]:
            for tl in tails:
                sys.stdout.write(f"{d}{sep}{a}{take}.{tl}\n")
                count += 1
print(f"{len(aliases)} aliases, {len(tails)} tails -> {count}", file=sys.stderr)
