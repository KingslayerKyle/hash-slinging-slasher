"""Two-axis grids found by splitting names at every underscore: head x tail.

For one family prefix (`vm_`, `ai_`, `pt_` ...), every confirmed name is cut at every `_` into a
head and a tail. A tail worn by at least MIN_HEADS heads is an *action*; a head wearing at least
MIN_TAILS actions is a *subject*. Every subject is then offered every action it does not yet wear.

Unlike a single-token swap this fills a hole in either axis from attested values on both, and
unlike the column cross product it does not need members to line up token for token, so
`vm_t9_ar_standard_reload_empty` and `vm_t9_sn_sniper_ads_in` belong to the same grid.

    python contrib/split_grid.py <named list> <prefix> [min_heads] [min_tails] [--size]
"""
import collections
import sys

path, prefix = sys.argv[1], sys.argv[2]
MIN_HEADS = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 8
MIN_TAILS = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 4

names = set()
for line in open(path, encoding="utf-8"):
    n = line.strip().split(",")[-1].lower()
    if n.startswith(prefix):
        names.add(n)

tail_heads = collections.defaultdict(set)
for n in names:
    cuts = [i for i, c in enumerate(n) if c == "_"]
    for i in cuts:
        head, tail = n[:i], n[i + 1:]
        if head and tail and len(head) > len(prefix):
            tail_heads[tail].add(head)

actions = {t for t, hs in tail_heads.items() if len(hs) >= MIN_HEADS}
head_tails = collections.defaultdict(set)
for t in actions:
    for h in tail_heads[t]:
        head_tails[h].add(t)
subjects = {h for h, ts in head_tails.items() if len(ts) >= MIN_TAILS}

total = len(subjects) * len(actions)
if "--axes" in sys.argv:
    # For a grid too big to print: write the two axes for confirm_plan (stem = subject + "_",
    # end = action) and let the compiled engine multiply them.
    out = sys.argv[sys.argv.index("--axes") + 1]
    with open(out + ".stems.txt", "w", encoding="utf-8") as f:
        f.write("".join(h + "_\n" for h in sorted(subjects)))
    with open(out + ".ends.txt", "w", encoding="utf-8") as f:
        f.write("".join(t + "\n" for t in sorted(actions)))
    print(f"{len(subjects)} subjects, {len(actions)} actions, {total:,} cells -> {out}.*", file=sys.stderr)
    sys.exit()

if "--size" in sys.argv:
    print(f"{len(names)} names, {len(actions)} actions, {len(subjects)} subjects, {total:,} cells",
          file=sys.stderr)
    sys.exit()

for h in sorted(subjects):
    for t in sorted(actions):
        n = f"{h}_{t}"
        if n not in names:
            print(n)
