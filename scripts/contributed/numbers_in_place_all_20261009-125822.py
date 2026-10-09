"""Every number in every known name swept to its neighbours, at the same width.

Method 4 (numbers in place) over every table generation, every merged submission and every local
finding: each digit run in a name -- `_03`, `v2`, `86x44x48`, `_1_1_n` -- is replaced, one run at a
time, by every value from 0 to max(original + `--above`, `--floor`) printed at the original width
(zero-padded where the original was). A family whose members are numbered gets its missing members.

Spent by: the corpus as it stands; re-run after any batch lands (every new name is a new family member).
With `--state`, a re-run expands only names it has not expanded before, so a snowball round costs
what the last round found rather than the whole corpus.
"""
from array import array
from pathlib import Path
import argparse
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
DIGITS = re.compile(r"\d+")
KINDS = ("xanims", "ximages", "xmaterials", "soundbanks_aliases", "xsounds")


def names():
    sources = [p for k in KINDS for p in (ROOT / "cod-name-db" / "csv").glob(f"fnv1a_{k}*.csv")]
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            sources.extend(p for p in base.rglob("*.txt") if not p.name.startswith("about"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            name = line.partition(",")[2].strip().lower()
            if name and "~" not in name and len(name) < 160:
                yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--above", type=int, default=12)
    ap.add_argument("--floor", type=int, default=12)
    ap.add_argument("--max-runs", type=int, default=3, help="skip names with more digit runs than this")
    ap.add_argument("--state", help="file of names already expanded; only new names are expanded, then it is updated")
    ap.add_argument("--seed-state", action="store_true", help="record every current name in --state and emit nothing")
    args = ap.parse_args()

    def key(name):
        return int.from_bytes(hashlib.blake2b(name.encode(), digest_size=8).digest(), "little")

    done = set()
    if args.state and Path(args.state).exists():
        done = set(array("Q", Path(args.state).read_bytes()))
    out = sys.stdout
    seen = set()
    emitted = 0
    for name in names():
        if name in seen:
            continue
        seen.add(name)
        if args.state:
            k = key(name)
            if k in done:
                continue
            done.add(k)
            if args.seed_state:
                continue
        runs = list(DIGITS.finditer(name))
        if not runs or len(runs) > args.max_runs:
            continue
        for m in runs:
            text = m.group()
            if len(text) > 4:
                continue
            width = len(text) if text.startswith("0") or len(text) > 1 else 1
            top = max(int(text) + args.above, args.floor)
            head, tail = name[:m.start()], name[m.end():]
            for v in range(0, top + 1):
                s = str(v).zfill(width)
                if s != text:
                    out.write(head + s + tail + "\n")
                    emitted += 1
    if args.state:
        Path(args.state).write_bytes(array("Q", done).tobytes())
    print(f"{len(seen):,} names, {emitted:,} candidates", file=sys.stderr)


if __name__ == "__main__":
    main()
