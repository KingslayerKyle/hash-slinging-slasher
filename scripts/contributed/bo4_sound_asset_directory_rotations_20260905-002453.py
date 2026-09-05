"""Rotate directory components of verified BO4 SAB sound paths, preserving file tail."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
def main():
    known = set(n.strip().replace("/", "\\") for n in snapshot.table_names("fnv1a_xsounds"))
    known |= set(n.strip().replace("/", "\\") for n in snapshot.confirmed_names("sound_asset"))
    out, seeds = set(), 0
    for name in known:
        parts = name.split("\\")
        if len(parts) < 4 or any(not x for x in parts): continue
        seeds += 1
        dirs, file = parts[:-1], parts[-1]
        for shift in range(1, len(dirs)):
            cand = "\\".join(dirs[shift:] + dirs[:shift] + [file])
            if cand not in known: out.add(cand)
    print(f"{seeds:,} sound seeds, {len(out):,} directory-rotation candidates", file=sys.stderr)
    for x in sorted(out): print(x)
if __name__ == "__main__": main()
