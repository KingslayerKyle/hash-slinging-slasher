"""Modern sound files completed as grids inside each directory and encoding tail.

The alias family grid returned thousands of aliases; sound files are the same names placed in a
folder with an encoding tail, so the grid has to be taken *within* a folder and tail or it
cross-mixes per-directory vocabularies (the reason MWII's whole-product sound plan found nothing).
A family is (directory, encoding tail, first `--head` basename tokens, token count); every middle
attested in it is crossed with every final token attested in it. Each candidate is offered with `/`
and with `.` separators, since titles differ in which their hash sees.

Spent by: the sound-file corpus as it stands; re-run after new sound files are confirmed.
"""
from collections import defaultdict
from pathlib import Path
import argparse
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')


def files():
    sources = [ROOT / "cod-name-db" / "csv" / "fnv1a_xsounds_v2.csv"]
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("sound_asset*.txt"))
            sources.extend(base.rglob("sndasset*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            name = line.partition(",")[2].strip().lower().replace("\\", "/")
            if not name:
                continue
            if "/" in name:
                folder, _, rest = name.rpartition("/")
                base, _, tail = rest.partition(".")
            else:
                parts = name.split(".")
                i = next((i for i in range(len(parts) - 1, -1, -1) if "_" in parts[i]), None)
                if i is None:
                    continue
                folder, base, tail = "/".join(parts[:i]), parts[i], ".".join(parts[i + 1:])
            if folder and tail:
                yield folder, base, tail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", type=int, default=2)
    ap.add_argument("--cap", type=int, default=50_000)
    args = ap.parse_args()

    middles, lasts = defaultdict(set), defaultdict(set)
    for folder, base, tail in files():
        tokens = base.split("_")
        if len(tokens) < args.head + 2:
            continue
        family = (folder, tail, "_".join(tokens[:args.head]), len(tokens))
        middles[family].add("_".join(tokens[args.head:-1]))
        lasts[family].add(tokens[-1])

    cells = 0
    for family in sorted(middles):
        m, l = middles[family], lasts[family]
        if len(m) < 2 or len(l) < 2 or len(m) * len(l) > args.cap:
            continue
        folder, tail, head, _ = family
        for middle in sorted(m):
            for last in sorted(l):
                slash = f"{folder}/{head}_{middle}_{last}.{tail}"
                print(slash)
                print(slash.replace("/", "."))
                cells += 2
    print(f"{cells:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
