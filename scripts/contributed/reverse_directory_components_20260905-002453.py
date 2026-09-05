"""Reverse the complete directory-component order of each non-sound asset name."""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(os.path.join(ROOT, "scripts", "snapshot.py")):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = (("fnv1a_xmodels", "xmodel"), ("fnv1a_xmaterials", "material"),
          ("fnv1a_ximages", "image"), ("fnv1a_xanims", "xanim"))
known = set()
for table, kind in TABLES:
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(kind))
seen = set()
for name in known:
    parts = name.split("/")
    if len(parts) < 3:
        continue
    candidate = "/".join(parts[:-1][::-1] + parts[-1:])
    if candidate not in known:
        seen.add(candidate)
print(f"{len(known)} known names; {len(seen)} reversed-directory candidates", file=sys.stderr)
for candidate in sorted(seen):
    print(candidate)
