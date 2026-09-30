"""Cores of recently confirmed names, crossed with every tail of every known name -- in rings by date.

On 2026-09-30 the 2,929 all-boundary cores cut from the 1,479 names this project confirmed in the
previous five days, crossed with all 5.2M boundary tails of every published or confirmed name,
returned 202 names from 30B candidates (one per ~150M). The same cores had already met the top-300k
uncarried endings through ab_snowball.py; what they had never met is the long tail of endings the
ranking cuts, which is exactly where a name's own relatives end.

A core cut from a name confirmed last week is a fragment of something real whose siblings are
probably unnamed too; a core cut from a name published two years ago has had every tool pointed at
it. So this walks outward by confirmation date, one ring at a time, skipping every core an earlier
ring (or the ledger) already crossed, and prints what each ring would cost so the walk can stop
where the density falls off.

    python contrib/core_rings.py --since 20260915 --until 20260924     write one ring's plan
    python contrib/core_rings.py --since 20260915 --until 20260924 --size-only

The ring's plan goes to plans/core_ring_<since>_<until>.txt; run it with confirm_plan per game.
Cores it writes are appended to contrib/core_rings_seen.txt so the next ring excludes them.
"""
from pathlib import Path
import argparse
import glob
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot

THIS_ERA = ["fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims",
            "fnv1a_xsounds", "fnv1a_soundbanks_aliases"]
SEEN = ROOT / "contrib" / "core_rings_seen.txt"
TAILS = ROOT / "contrib" / "all_tails.txt"


def norm(name):
    return name.strip().lower().replace("\\", "/").encode("utf-8")


def confirmed_between(since, until):
    names = set()
    for game in ("blkopscw", "blkops04"):
        for folder in glob.glob(str(ROOT / "findings" / game / "run_*")):
            match = re.search(r"run_(\d{8})", folder)
            if match and since <= match.group(1) <= until:
                for path in glob.glob(folder + "/*.txt"):
                    with open(path, encoding="utf-8", errors="ignore") as handle:
                        for line in handle:
                            if line.strip():
                                names.add(norm(line.split(",", 1)[-1]))
    return names


def cores_of(names):
    out = set()
    for name in names:
        for index, character in enumerate(name):
            if character in b"_/" and index > 0:
                out.add(name[:index])
    return out


def all_tails():
    tails = set()
    for name in snapshot.table_names(*THIS_ERA) + snapshot.confirmed_names():
        name = norm(name)
        for index, character in enumerate(name):
            if character in b"_/" and 0 < index < len(name) - 1:
                tails.add(name[index:])
    return tails


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", required=True, help="YYYYMMDD, inclusive")
    parser.add_argument("--until", required=True, help="YYYYMMDD, inclusive")
    parser.add_argument("--size-only", action="store_true")
    args = parser.parse_args()

    names = confirmed_between(args.since, args.until)
    seen = set()
    if SEEN.exists():
        seen = {line.strip() for line in open(SEEN, "rb") if line.strip()}
    cores = sorted(cores_of(names) - seen)

    if not TAILS.exists():
        tails = sorted(all_tails())
        TAILS.write_bytes(b"\n".join(tails) + b"\n")
    tail_count = sum(1 for _ in open(TAILS, "rb"))

    print(f"{len(names):,} names confirmed {args.since}-{args.until}, {len(cores):,} cores not "
          f"crossed before, x {tail_count:,} tails = {len(cores) * tail_count / 1e9:.1f}B per game")
    if args.size_only or not cores:
        return 0

    stem = f"core_ring_{args.since}_{args.until}"
    (ROOT / "contrib" / f"{stem}.txt").write_bytes(b"\n".join(cores) + b"\n")
    (ROOT / "plans" / f"{stem}.txt").write_text(
        f"label: core ring {args.since}-{args.until} x all tails\n"
        f"describe: core_rings.py -- all-boundary cores of names confirmed {args.since} to "
        f"{args.until} not crossed by an earlier ring, x every tail of every known name\n"
        f"stem: @contrib/{stem}.txt\nend: @contrib/{TAILS.name}\nbare: yes\nfold: yes\n",
        encoding="utf-8")
    with open(SEEN, "ab") as handle:
        handle.write(b"\n".join(cores) + b"\n")
    print(f"wrote plans/{stem}.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
