"""Write one game's split-grid axes -- every family of every wanted pool -- for confirm_plan.

The subjects (heads + "_") and actions (tails) of contrib/split_grid.py, unioned over each family
of at least --min-family confirmed names. Crossing one game's subjects with the *other* game's
actions asks whether a convention one title uses for a subject the other title also has was
carried across -- which neither verbatim transfer (whole names) nor a single-game grid can reach.

    python contrib/split_axes_all.py --game BLKOPS04 --out plans/axes_bo4
    -> plans/axes_bo4.stems.txt, plans/axes_bo4.ends.txt

Reads logs/named_<game>_<pool>.txt as written by contrib/pool_named_dump.py --dump.
"""
import argparse
import collections
import os

UNH = os.path.dirname(os.path.abspath(__file__))
while UNH != os.path.dirname(UNH) and not os.path.isfile(os.path.join(UNH, "scripts", "snapshot.py")):
    UNH = os.path.dirname(UNH)
POOLS = ["image", "material", "xmodel", "xanim", "sound_alias"]

ap = argparse.ArgumentParser()
ap.add_argument("--game", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--min-family", type=int, default=300)
ap.add_argument("--min-heads", type=int, default=8)
ap.add_argument("--min-tails", type=int, default=4)
args = ap.parse_args()

all_subjects, all_actions = set(), set()
for pool in POOLS:
    path = os.path.join(UNH, "logs", f"named_{args.game.lower()}_{pool}.txt")
    names = {line.strip() for line in open(path, encoding="utf-8") if "_" in line}
    fams = collections.defaultdict(set)
    for n in names:
        fams[n.split("_")[0] + "_"].add(n)
    for fam, members in fams.items():
        if len(members) < args.min_family:
            continue
        tail_heads = collections.defaultdict(set)
        for n in members:
            for i, c in enumerate(n):
                if c == "_" and i > len(fam) and i + 1 < len(n):
                    tail_heads[n[i + 1:]].add(n[:i])
        actions = {t for t, hs in tail_heads.items() if len(hs) >= args.min_heads}
        head_tails = collections.defaultdict(set)
        for t in actions:
            for h in tail_heads[t]:
                head_tails[h].add(t)
        all_subjects |= {h for h, ts in head_tails.items() if len(ts) >= args.min_tails}
        all_actions |= actions

with open(args.out + ".stems.txt", "w", encoding="utf-8") as f:
    f.write("".join(h + "_\n" for h in sorted(all_subjects)))
with open(args.out + ".ends.txt", "w", encoding="utf-8") as f:
    f.write("".join(t + "\n" for t in sorted(all_actions)))
print(f"{args.game}: {len(all_subjects)} subjects, {len(all_actions)} actions -> {args.out}.*")
