"""Tails of length k over every table generation -- the modern `_v2` tables included.

`scripts/tails.py` (method 17) builds its stems from the v1 tables and confirmed names only, so on
the modern titles it never cut a single published `_v2` name. This is the same method -- every known
name with its last k characters replaced by every k-character string over the measured alphabet --
with stems from every `fnv1a_*` table (v1 and v2), every merged submission and every local finding.
It writes a plan; `confirm_plan` does the multiplying.

    python contrib/tails_every_table.py --length 3 --write-plan plans/tails3_all.txt
    confirm_plan plans/tails3_all.txt --game BLACKOP7

Spent by: the corpus as it stands, per length; re-run after it grows.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import argparse
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
KINDS = ("xanims", "ximages", "xmaterials", "soundbanks_aliases", "xsounds")


def names():
    sources = [p for k in KINDS for p in (ROOT / "cod-name-db" / "csv").glob(f"fnv1a_{k}*.csv")]
    for folder in ("submissions", "findings", "all_names"):
        base = ROOT / folder
        if base.exists():
            sources.extend(p for p in base.rglob("*.txt") if not p.name.startswith("about"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower().replace("\\", "/")
            if name and "~" not in name and len(name) < 200:
                yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--length", type=int, default=3)
    ap.add_argument("--alphabet", type=int, default=37)
    ap.add_argument("--write-plan", required=True)
    args = ap.parse_args()

    stems, counted = set(), Counter()
    for name in names():
        counted.update(name[-4:])
        if len(name) > args.length + 3:
            stems.add(name[:-args.length])
    alphabet = [c for c, _ in counted.most_common(args.alphabet)]

    plan = ROOT / args.write_plan
    base = plan.with_suffix("")
    (base.parent / (base.name + ".stems.txt")).write_text("\n".join(sorted(stems)) + "\n")
    (base.parent / (base.name + ".endings.txt")).write_text(
        "\n".join("".join(p) for p in product(alphabet, repeat=args.length)) + "\n")
    rel = base.relative_to(ROOT).as_posix()
    plan.write_text(
        f"label: tails of length {args.length}, every table generation\n"
        f"describe: every known name (v1 and v2 tables, submissions, findings) cut short by "
        f"{args.length}, against every {args.length}-character ending over {len(alphabet)} characters\n"
        f"stem: @{rel}.stems.txt\nend: @{rel}.endings.txt\nbare: yes\nfold: yes\n")
    print(f"{len(stems):,} stems x {len(alphabet) ** args.length:,} endings; alphabet {''.join(alphabet)}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
