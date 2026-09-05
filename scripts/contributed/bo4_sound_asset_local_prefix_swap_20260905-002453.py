"""Swap sound-file basename prefixes only within an attested directory/tail family."""
import collections, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

def main():
    known = set(n.strip().replace("/", "\\") for n in snapshot.table_names("fnv1a_xsounds"))
    known |= set(n.strip().replace("/", "\\") for n in snapshot.confirmed_names("sound_asset"))
    groups = collections.defaultdict(lambda: collections.defaultdict(set))
    seeds = 0
    for name in known:
        path, dot, ext = name.rpartition(".")
        if not dot or "\\" not in path: continue
        directory, _, base = path.rpartition("\\")
        toks = base.split("_")
        if len(toks) < 3 or not all(toks): continue
        seeds += 1
        groups[(directory, ext, tuple(toks[-1:]))]["_".join(toks[:-1])].add(name)
    out = set()
    for (directory, ext, tail), prefixes in groups.items():
        if len(prefixes) < 2: continue
        for prefix in prefixes:
            for other in prefixes:
                if prefix == other: continue
                candidate = directory + "\\" + other + "_" + "_".join(tail) + "." + ext
                if candidate not in known: out.add(candidate)
    print(f"{seeds:,} sound seeds, {len(out):,} local-prefix swap candidates", file=sys.stderr)
    for name in sorted(out): print(name)
if __name__ == "__main__": main()
