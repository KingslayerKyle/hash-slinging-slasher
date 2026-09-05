"""Reverse underscore-token order in verified BO4 SAB sound basenames.

This tests a structural mirror relation while preserving the native unfolded path
and the recording's dotted tail.  It is deliberately limited to sound_asset
names, whose separator form is significant in BO4.
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

GAME = "BLKOPS04"
snap = snapshot.read(os.path.join(ROOT, "snapshots", GAME.lower() + ".ids"))
wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
seeds = set()
for table in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
    with open(table, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            _, _, name = line.partition(",")
            name = name.strip()
            if name and snapshot.fnv1a_nofold(name) & snapshot.ID_MASK in wanted:
                seeds.add(name)
seeds.update(snapshot.confirmed_names("sound_asset"))

count = 0
for name in sorted(seeds):
    cut = max(name.rfind("/"), name.rfind("\\")) + 1
    head, base = name[:cut], name[cut:]
    dot = base.find(".")
    if dot <= 0:
        continue
    core, tail = base[:dot], base[dot:]
    parts = core.split("_")
    if len(parts) < 2:
        continue
    mirrored = "_".join(reversed(parts))
    if mirrored != core:
        print(head + mirrored + tail)
        count += 1
print(f"{GAME}: {len(seeds)} seeds, {count} token-mirror candidates", file=sys.stderr)
