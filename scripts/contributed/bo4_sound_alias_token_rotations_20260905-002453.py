"""Rotate token sequences in verified BO4 sound-alias names."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot
def main():
    known = set(n.strip().lower() for n in snapshot.table_names("fnv1a_soundbanks_aliases"))
    known |= set(n.strip().lower() for n in snapshot.confirmed_names("sound_alias"))
    out, seeds = set(), 0
    for name in known:
        if "/" in name or "\\" in name or "." in name: continue
        toks = name.split("_")
        if len(toks) < 4 or not all(toks): continue
        seeds += 1
        for shift in range(1, len(toks)):
            cand = "_".join(toks[shift:] + toks[:shift])
            if cand not in known: out.add(cand)
    print(f"{seeds:,} alias seeds, {len(out):,} cyclic-rotation candidates", file=sys.stderr)
    for x in sorted(out): print(x)
if __name__ == "__main__": main()
