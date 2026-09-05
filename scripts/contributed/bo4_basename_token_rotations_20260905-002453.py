"""Rotate complete basename token sequences from verified BO4 non-sound names."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims", "fnv1a_xmodels")

def main():
    known = set()
    for table in TABLES:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    for pool in ("image", "material", "anim", "model"):
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(pool))
    candidates = set()
    seeds = 0
    for name in known:
        if "/" in name or "." in name:
            continue
        tokens = name.split("_")
        if len(tokens) < 4 or not all(tokens):
            continue
        seeds += 1
        for shift in range(1, len(tokens)):
            cand = "_".join(tokens[shift:] + tokens[:shift])
            if cand not in known:
                candidates.add(cand)
    print(f"{seeds:,} seeds, {len(candidates):,} cyclic-rotation candidates", file=sys.stderr)
    for candidate in sorted(candidates):
        print(candidate)

if __name__ == "__main__":
    main()
