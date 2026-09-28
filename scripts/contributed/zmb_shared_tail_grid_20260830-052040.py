"""Fill the measured zmb family using tails shared by multiple observed axes."""
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
    known = {n.strip().lower().replace("\\", "/") for n in snapshot.table_names(*TABLES)}
    known |= {n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names()}
    observed = [(parts[1], parts[2]) for name in known if name.startswith("zmb_")
                and "/" not in name and "." not in name
                for parts in [name.split("_", 2)] if len(parts) == 3 and parts[1] and parts[2]]
    axes = {axis for axis, _ in observed}
    tails = {tail for tail, count in collections.Counter(tail for _, tail in observed).items()
             if count > 1}
    candidates = sorted({f"zmb_{axis}_{tail}" for axis in axes for tail in tails} - known)
    print(f"zmb shared-tail grid: {len(axes):,} axes x {len(tails):,} tails = "
          f"{len(candidates):,} unseen cells", file=sys.stderr)
    for candidate in candidates:
        print(candidate)


if __name__ == "__main__":
    main()
