"""Run split_grid over every sizeable family of every wanted pool of one game.

Families are the first `_`-token (with any directory) of the confirmed names; a family needs at
least --min-family names to have a measurable grid. The named lists are read from the published
csv by hash column plus this clone's findings, exactly as contrib/pool_named_dump.py does.

    python contrib/split_grid_all.py --game BLKOPSCW | bin\\windows\\confirm_list.exe - --game BLKOPSCW ...
"""
import argparse
import collections
import glob
import os
import subprocess
import sys

UNH = os.path.dirname(os.path.abspath(__file__))
while UNH != os.path.dirname(UNH) and not os.path.isfile(os.path.join(UNH, "scripts", "snapshot.py")):
    UNH = os.path.dirname(UNH)
sys.path.insert(0, os.path.join(UNH, "scripts"))
import snapshot  # noqa: E402

POOLS = {
    "image": "fnv1a_ximages",
    "material": "fnv1a_xmaterials",
    "xmodel": "fnv1a_xmodels",
    "xanim": "fnv1a_xanims",
    "sound_alias": "fnv1a_soundbanks_aliases",
}
MASK = (1 << 63) - 1

ap = argparse.ArgumentParser()
ap.add_argument("--game", required=True)
ap.add_argument("--min-family", type=int, default=300)
ap.add_argument("--min-heads", type=int, default=8)
ap.add_argument("--min-tails", type=int, default=4)
ap.add_argument("--max-cells", type=int, default=3_000_000, help="skip a family grid larger than this")
args = ap.parse_args()

snap = snapshot.read(os.path.join(UNH, "snapshots", args.game.lower() + ".ids"))
by_pool = snap.by_pool()
tmp = os.path.join(UNH, "logs", "split_grid_tmp.txt")
# split_grid.py sits beside this file; once promoted it carries a timestamp (split_grid_<stamp>.py).
HERE = os.path.dirname(os.path.abspath(__file__))
SPLIT = sorted(p for p in glob.glob(os.path.join(HERE, "split_grid*.py")) if "split_grid_all" not in p)[0]

for pool, csv in POOLS.items():
    ids = set(by_pool[pool])
    names = set()
    with open(os.path.join(UNH, "cod-name-db", "csv", csv + ".csv"), encoding="utf-8", errors="replace") as f:
        for line in f:
            h, _, n = line.rstrip("\n").partition(",")
            try:
                if int(h, 16) & MASK in ids:
                    names.add(n.lower())
            except ValueError:
                pass
    for path in glob.glob(os.path.join(UNH, "findings", "*", pool + ".txt")):
        for line in open(path, encoding="utf-8", errors="replace"):
            n = line.strip().split(",")[-1].lower()
            if snapshot.fnv1a(n) & MASK in ids:
                names.add(n)
    fams = collections.Counter(n.split("_")[0] + "_" for n in names if "_" in n)
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("\n".join(names) + "\n")
    for fam, count in fams.most_common():
        if count < args.min_family:
            break
        size = subprocess.run([sys.executable, SPLIT, tmp, fam,
                               str(args.min_heads), str(args.min_tails), "--size"],
                              capture_output=True, text=True).stderr.strip()
        cells = int(size.rsplit(" ", 2)[-2].replace(",", "")) if "cells" in size else 0
        print(f"{args.game} {pool:12} {fam:16} {size}" + ("  SKIPPED" if cells > args.max_cells else ""),
              file=sys.stderr)
        if 0 < cells <= args.max_cells:
            out = subprocess.run([sys.executable, SPLIT, tmp, fam,
                                  str(args.min_heads), str(args.min_tails)], capture_output=True, text=True)
            sys.stdout.write(out.stdout)
os.remove(tmp)
