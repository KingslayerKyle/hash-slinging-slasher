"""Target combinations of uncarried leading heads and frequent uncarried tail atoms."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

TABLES = ("fnv1a_xmaterials", "fnv1a_xmaterials_v2", "fnv1a_ximages",
          "fnv1a_ximages_v2", "fnv1a_xanims", "fnv1a_xmodels",
          "fnv1a_soundbanks_aliases", "fnv1a_xsounds")
TAILS = ("futz", "kill", "nag", "hv", "exerts", "greet", "riot", "stab")

def main():
    known = set()
    for table in TABLES:
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.table_names(table))
    for pool in ("image", "material", "anim", "model", "sound_alias", "sound_asset"):
        known.update(n.strip().lower().replace("\\", "/") for n in snapshot.confirmed_names(pool))
    with (ROOT / "data" / "prefixes.txt").open(encoding="utf-8", errors="replace") as f:
        carried = {line.strip().lower() for line in f if line.strip()}
    heads = set()
    for name in known:
        if "/" in name or "." in name or "_" not in name:
            continue
        head = name.split("_", 1)[0] + "_"
        if not any(head[:cut] in carried for cut in range(1, len(head) + 1)):
            heads.add(head)
    candidates = set()
    for name in known:
        if name.split("_", 1)[0] + "_" not in heads:
            continue
        base, sep, _ = name.rpartition("_")
        if not sep or not base:
            continue
        for tail in TAILS:
            cand = base + "_" + tail
            if cand not in known:
                candidates.add(cand)
    print(f"{len(heads):,} uncarried heads x {len(TAILS)} uncarried tail atoms -> {len(candidates):,} candidates", file=sys.stderr)
    for cand in sorted(candidates):
        print(cand)

if __name__ == "__main__":
    main()
