"""Generate Cold War candidates by translating BO4 T8 asset tags to T9.

The two games share the asset naming grammar but their title-era tag is often embedded
in the basename.  This deliberately tests only exact observed BO4 spellings with the
single tag substitution, rather than inventing arbitrary word combinations.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmodels_v2", "fnv1a_xmaterials", "fnv1a_xmaterials_v2",
          "fnv1a_ximages", "fnv1a_ximages_v2", "fnv1a_xanims", "fnv1a_xanims_v2")

def norm(value):
    return value.strip().lower().replace("\\", "/")

names = {norm(n) for n in snapshot.table_names(*TABLES) if n.strip()}
names.update(norm(n) for n in snapshot.confirmed_names() if n.strip())
out = set()
for name in names:
    # Require a real T8-era token boundary.  This excludes arbitrary words containing t8.
    if re.search(r"(?:^|[_/])t8(?:[_/]|$)", name):
        candidate = re.sub(r"(^|[_/])t8(?=[_/]|$)", r"\1t9", name)
        if candidate != name:
            out.add(candidate)
print(f"{len(names):,} known names -> {len(out):,} T8-to-T9 candidates", file=sys.stderr)
for name in sorted(out):
    print(name)
