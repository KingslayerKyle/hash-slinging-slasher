"""Test the direct BO4 material-to-image basename naming convention."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot


def main():
    materials = set(snapshot.table_names("fnv1a_xmaterials"))
    materials.update(snapshot.confirmed_names(kind="material"))
    seeds = set()
    for raw in materials:
        name = raw.strip().lower().replace("\\", "/")
        if name.startswith("mtl_") and len(name) > 4:
            seeds.add(name)
    candidates = {"i_" + name[4:] for name in seeds}
    print(f"{len(seeds):,} verified mtl_ seeds, {len(candidates):,} direct image candidates", file=sys.stderr)
    for candidate in sorted(candidates):
        print(candidate)


if __name__ == "__main__":
    main()
