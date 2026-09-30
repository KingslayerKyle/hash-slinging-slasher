"""A second slotswap substitution, applied only to substituted cores the game has confirmed.

slotswap_cores.py substitutes one interior token of an all-boundary core and crosses the result with
the ending lists; over 2026-09-26..30 that confirmed ~450 names across both games. Each of those
names begins with a substituted core that is now known to be real -- and a core family that just
proved to vary in one slot is the likeliest place for a sibling that varies in another.
Substituting every core again would be ~35M^2; substituting only the confirmed ones is a few
thousand, which is the fresh-family result (core_rings.py) applied to the substitution generator
instead of to the cut point.

    python contrib/second_swap.py            write contrib/second_swap_cores.txt and a plan
"""
from pathlib import Path
import glob
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "contrib"))
import snapshot
import slotswap_cores as sc


def lines(path):
    with open(path, "rb") as handle:
        return {line.strip().decode("utf-8", "ignore") for line in handle if line.strip()}


def main():
    swapped = lines(ROOT / "contrib" / "slotswap_cores_new.txt") | lines(
        ROOT / "contrib" / "slotswap_sound_cores_new.txt")
    found = set()
    for folder in sorted(glob.glob(str(ROOT / "findings" / "*" / "run_*_plan"))):
        notes = Path(folder) / "notes.md"
        if not notes.exists() or "slotswap" not in notes.read_text(encoding="utf-8",
                                                                    errors="ignore"):
            continue
        for path in glob.glob(folder + "/*.txt"):
            with open(path, encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    if line.strip():
                        found.add(line.split(",", 1)[-1].strip().lower().replace("\\", "/"))

    # The substituted core each find was built on: its longest prefix in the swapped list.
    proven = set()
    for name in found:
        for index in range(len(name) - 1, 0, -1):
            if name[index] in "_/" and name[:index] in swapped:
                proven.add(name[:index])
                break

    corpus = snapshot.table_names(*sc.THIS_ERA) + snapshot.confirmed_names()
    corpus = [n.strip().lower().replace("\\", "/") for n in corpus if n.strip()]
    offers = sc.measure_offers(corpus)
    second = set()
    for core in proven:
        second |= sc.substituted_cores(core, offers)
    second -= swapped
    base = lines(ROOT / "contrib" / "ab_cores.txt")
    second -= base

    out = ROOT / "contrib" / "second_swap_cores.txt"
    out.write_text("\n".join(sorted(second)) + "\n", encoding="utf-8")
    print(f"{len(found):,} names from slotswap runs, {len(proven):,} proven substituted cores, "
          f"{len(second):,} second-substitution cores not searched before", file=sys.stderr)


if __name__ == "__main__":
    main()
