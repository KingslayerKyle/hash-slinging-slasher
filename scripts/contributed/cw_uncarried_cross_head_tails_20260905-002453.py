"""Combine uncarried basename heads with tails proven under several carried heads.

Unlike the local-grid pass, the tail is learned across different families; requiring
multiple independent heads keeps this a bounded, evidenced cross-family probe.
"""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages",
          "fnv1a_ximages_v2", "fnv1a_xanims", "fnv1a_xmodels",
          "fnv1a_soundbanks_aliases", "fnv1a_xsounds")
POOLS = ("image", "material", "anim", "model", "sound_alias", "sound_asset")

def main():
    known = set()
    for table in TABLES:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    for pool in POOLS:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(pool))
    carried = {line.strip().lower() for line in (ROOT / "data" / "prefixes.txt").open(encoding="utf-8") if line.strip()}
    uncarried = set()
    tail_heads = collections.defaultdict(set)
    for name in known:
        if "/" in name or "." in name or "_" not in name:
            continue
        head, tail = name.split("_", 1)
        head += "_"
        if not any(head[:cut] in carried for cut in range(1, len(head) + 1)):
            uncarried.add(head)
        else:
            tail_heads[tail].add(head)
    # A tail must be independently present under at least three carried heads.
    shared = {tail for tail, heads in tail_heads.items() if len(heads) >= 3}
    candidates = {head + tail for head in uncarried for tail in shared
                  if head + tail not in known}
    print(f"{len(uncarried):,} uncarried heads, {len(shared):,} cross-head tails, {len(candidates):,} candidates", file=sys.stderr)
    for candidate in sorted(candidates):
        print(candidate)

if __name__ == "__main__":
    main()
