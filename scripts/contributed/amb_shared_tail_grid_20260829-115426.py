"""Fill the measured amb family grid using tails shared by multiple axes."""
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import snapshot

TABLES = (
    "fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages", "fnv1a_ximages_v2",
    "fnv1a_xmodels", "fnv1a_xmodels_v2", "fnv1a_xanims", "fnv1a_xanims_v2",
    "fnv1a_soundbanks_aliases", "fnv1a_soundbanks_aliases_v2",
    "fnv1a_xsounds", "fnv1a_xsounds_v2",
)


def main():
    have = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES)}
    have |= {n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names()}
    observed = []
    for name in have:
        if name.count("_") < 2 or "/" in name or "." in name:
            continue
        head, axis, tail = name.split("_", 2)
        if head == "amb" and axis and tail:
            observed.append((axis, tail))
    axes = {axis for axis, _ in observed}
    counts = collections.Counter(tail for _, tail in observed)
    tails = {tail for tail, count in counts.items() if count > 1}
    candidates = sorted({f"amb_{axis}_{tail}" for axis in axes for tail in tails} - have)
    print(f"amb shared-tail grid: {len(axes):,} axes x {len(tails):,} tails = "
          f"{len(candidates):,} unseen cells", file=sys.stderr)
    for candidate in candidates:
        print(candidate)


if __name__ == "__main__":
    main()
