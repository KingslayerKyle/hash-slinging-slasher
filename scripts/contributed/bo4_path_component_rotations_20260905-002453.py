"""Rotate complete directory-component sequences of verified BO4 non-sound paths."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims", "fnv1a_xmodels")
def main():
    known = set()
    for t in TABLES:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(t))
    for p in ("image", "material", "anim", "model"):
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(p))
    out, seeds = set(), 0
    for name in known:
        parts = name.split("/")
        if len(parts) < 3 or any(not x or "." in x for x in parts):
            continue
        seeds += 1
        dirs, base = parts[:-1], parts[-1]
        for shift in range(1, len(dirs)):
            candidate = "/".join(dirs[shift:] + dirs[:shift] + [base])
            if candidate not in known:
                out.add(candidate)
    print(f"{seeds:,} path seeds, {len(out):,} directory-rotation candidates", file=sys.stderr)
    for name in sorted(out): print(name)
if __name__ == "__main__": main()
