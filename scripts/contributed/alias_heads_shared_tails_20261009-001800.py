"""Write a confirm_plan for sound aliases: every known head x every tail shared by >= N heads.

Every modern title hashes its aliases with the same offset and keeps them flat, so an alias known
for any game is legal vocabulary for every other. MWII's shared-tail plan (`MWII_SOUND_METHODS`)
returned 1 name per 14,800 candidates -- but it only ever hunted MWII's ids. This builds the same
head x shared-tail product from every alias anybody knows, in every game, and writes it as a plan
so it can be pointed at any game with `confirm_plan --game <TAG>`.

A head is the tokens before an underscore cut (kept with its trailing `_`); a tail is the tokens
after it. A tail is carried only when at least `--support` distinct heads attest it, so it is
repetition that exists rather than a word that occurred once.

    python contrib/alias_heads_shared_tails.py --support 2
    confirm_plan plans/alias_heads_tails.txt --game YAMYAMOK

Spent by: a target game whose alias ids have been offered this product at this support level;
widening the vocabulary after a first pass buys little (MWII: 2,121 -> 2,048 -> 1,720, mostly claimed).
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parent.parent


def aliases():
    sources = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_soundbanks_aliases*.csv"))
    for folder in ("submissions", "findings", "all_names"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("sound_alias*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower()
            if name and "/" not in name and "\\" not in name and len(name) < 120:
                yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--support", type=int, default=2)
    ap.add_argument("--max-tail-tokens", type=int, default=4)
    ap.add_argument("--out", default="plans/alias_heads_tails")
    args = ap.parse_args()

    heads, tail_heads = set(), defaultdict(set)
    count = 0
    for name in set(aliases()):
        count += 1
        tokens = name.split("_")
        for k in range(1, len(tokens)):
            head = "_".join(tokens[:k]) + "_"
            tail = "_".join(tokens[k:])
            heads.add(head)
            if len(tokens) - k <= args.max_tail_tokens:
                tail_heads[tail].add(head)

    tails = sorted(t for t, h in tail_heads.items() if len(h) >= args.support and t)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    (out.parent / (out.name + ".heads.txt")).write_text("\n".join(sorted(heads)) + "\n")
    (out.parent / (out.name + ".tails.txt")).write_text("\n".join(tails) + "\n")
    (out.parent / (out.name + ".txt")).write_text(
        f"label: alias heads x shared tails, every game's aliases (support >= {args.support})\n"
        "describe: every known alias head crossed with tails attested under several heads\n"
        f"stem: @{args.out}.heads.txt\n"
        f"end: @{args.out}.tails.txt\n"
        "bare: yes\n"
        "fold: yes\n"
    )
    print(f"{count:,} aliases -> {len(heads):,} heads x {len(tails):,} tails = "
          f"{len(heads) * len(tails):,}", file=sys.stderr)


if __name__ == "__main__":
    main()
