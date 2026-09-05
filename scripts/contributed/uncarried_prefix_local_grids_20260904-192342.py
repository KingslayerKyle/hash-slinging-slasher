"""Fill locally attested tail grids under prefixes absent from the prefix ceiling."""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = (
    "fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages",
    "fnv1a_ximages_v2", "fnv1a_xanims", "fnv1a_xmodels",
    "fnv1a_soundbanks_aliases", "fnv1a_xsounds",
)

def main():
    known = set()
    for table in TABLES:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    for pool in ("image", "material", "anim", "model", "sound_alias", "sound_asset"):
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(pool))
    with (ROOT / "data" / "prefixes.txt").open(encoding="utf-8", errors="replace") as f:
        carried = {line.strip().lower() for line in f if line.strip()}
    heads = collections.defaultdict(list)
    for name in known:
        if "/" in name or "." in name:
            continue
        first = name.split("_", 1)[0] + "_" if "_" in name else ""
        if first and not any(first[:cut] in carried for cut in range(1, len(first) + 1)):
            heads[first].append(name)
    candidates = set()
    selected = 0
    for head, names in heads.items():
        axes = set()
        tails = collections.Counter()
        for name in names:
            rest = name[len(head):]
            axis, sep, tail = rest.partition("_")
            if sep and axis and tail:
                axes.add(axis)
                tails[tail] += 1
        shared = {tail for tail, count in tails.items() if count > 1}
        if len(axes) < 2 or not shared:
            continue
        selected += 1
        for axis in axes:
            for tail in shared:
                cand = head + axis + "_" + tail
                if cand not in known:
                    candidates.add(cand)
    print(f"{selected:,} uncarried prefixes, {len(candidates):,} local grid cells", file=sys.stderr)
    for cand in sorted(candidates):
        print(cand)

if __name__ == "__main__":
    main()
