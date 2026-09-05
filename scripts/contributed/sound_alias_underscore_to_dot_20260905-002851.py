"""Probe sound aliases formed by replacing one observed underscore separator with a dot."""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot
known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names("fnv1a_soundbanks_aliases")}
known |= {n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names("sound_alias")}
seen = set()
for name in known:
    for i, char in enumerate(name):
        if char == "_":
            candidate = name[:i] + "." + name[i + 1:]
            if candidate not in known:
                seen.add(candidate)
print(f"{len(known)} known sound aliases; {len(seen)} underscore-to-dot candidates", file=sys.stderr)
for candidate in sorted(seen):
    print(candidate)
