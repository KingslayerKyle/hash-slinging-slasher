"""Profile the named assets of one pool: first token, last token, special chars.

Reads the published csv by its hash column (not by re-hashing names) plus this clone's findings.
"""
import collections
import glob
import os
import sys

UNH = os.path.dirname(os.path.abspath(__file__))
while UNH != os.path.dirname(UNH) and not os.path.isfile(os.path.join(UNH, "scripts", "snapshot.py")):
    UNH = os.path.dirname(UNH)
sys.path.insert(0, os.path.join(UNH, "scripts"))
import snapshot  # noqa: E402

GAME = sys.argv[1] if len(sys.argv) > 1 else "blkopscw"
POOL = sys.argv[2] if len(sys.argv) > 2 else "image"
CSV = sys.argv[3] if len(sys.argv) > 3 else "fnv1a_ximages"
MASK = (1 << 63) - 1

snap = snapshot.read(os.path.join(UNH, "snapshots", f"{GAME}.ids"))
ids = set(snap.by_pool()[POOL])

names = {}
with open(os.path.join(UNH, "cod-name-db", "csv", CSV + ".csv"), encoding="utf-8", errors="replace") as f:
    for line in f:
        h, _, n = line.rstrip("\n").partition(",")
        try:
            v = int(h, 16) & MASK
        except ValueError:
            continue
        if v in ids:
            names[v] = n.lower()
tag = {"blkopscw": "BLKOPSCW", "blkops04": "BLKOPS04"}[GAME]
for path in glob.glob(os.path.join(UNH, "findings", tag.lower(), POOL + ".txt")) + glob.glob(
        os.path.join(UNH, "findings", "*", POOL + ".txt")):
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            n = line.strip().split(",")[-1]
            v = snapshot.fnv1a(n) & MASK
            if v in ids:
                names[v] = n.lower()
print(f"{GAME} {POOL}: {len(ids)} ids, {len(names)} named")

if "--dump" in sys.argv:
    out = os.path.join(UNH, "logs", f"named_{GAME}_{POOL}.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(names.values())) + "\n")
    print("wrote", out)

first = collections.Counter()
last = collections.Counter()
chars = collections.Counter()
for n in names.values():
    first[n.split("_")[0][:14]] += 1
    last[n.rsplit("_", 1)[-1][:10]] += 1
    for c in set(n):
        if not c.isalnum() and c != "_":
            chars[c] += 1
print("special chars:", chars.most_common(12))
print("first tokens:", first.most_common(40))
print("last tokens:", last.most_common(40))
