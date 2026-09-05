"""Interior character substitutions for the second verified CW sound-asset seed slice."""
import glob, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

GAME = "BLKOPSCW"
START, LIMIT = 2000, 2000
snap = snapshot.read(os.path.join(ROOT, "snapshots", "blkopscw.ids"))
wanted = {aid for aid, pool in snap.records if snap.pool_name(pool) == "sound_asset"}
names = set()
for table in glob.glob(os.path.join(ROOT, "cod-name-db", "csv", "*xsounds*.csv")):
    with open(table, encoding="utf-8", errors="replace") as h:
        for line in h:
            _, _, name = line.partition(",")
            name = name.strip()
            if name and snapshot.fnv1a(name) & snapshot.ID_MASK in wanted:
                names.add(name)
names.update(snapshot.confirmed_names("sound_asset"))
seeds = sorted(n.strip() for n in names if n.strip())[START:START + LIMIT]
alphabet = "0123456789abcdefghijklmnopqrstuvwxyz_-"
emitted = 0
for name in seeds:
    cut = max(name.rfind("/"), name.rfind("\\")) + 1
    head, base = name[:cut], name[cut:]
    dot = base.find(".")
    if dot <= 0:
        continue
    core, tail = base[:dot], base[dot:]
    for i, old in enumerate(core):
        for char in alphabet:
            if char != old:
                print(head + core[:i] + char + core[i + 1:] + tail)
                emitted += 1
print(f"{GAME}: seeds {START+1}-{START+len(seeds)}, {len(seeds)} seeds, {emitted} candidates", file=sys.stderr)
