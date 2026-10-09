"""Modern sound files offered under every encoding tail their siblings use.

A modern sound file ends in an encoding tail -- `.tnn.75.48000.all`, `.snn.20.48000.english`,
`.lnn.85.48000.all` (measured on 108,130 named BO7 files: 25 tails cover all but a handful). The
same stem is often encoded more than once, so every named stem is offered under the 40 most common
tails. Invented by a parallel BLACKOP7 worker session (+35 on BO7). `--dotted` also spells each
stem with `.` separators, which MWII/MWIII hash (the tables display `/`).

Spent by: the named sound-file corpus as it stands; re-run after it grows.
"""
import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
R = re.compile(r"^(.*)(\.[a-z]+\.\d+\.\d+\.[a-z_]+)$")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dotted", action="store_true")
    a = ap.parse_args()
    srcs = list((ROOT / "cod-name-db" / "csv").glob("*sound*.csv"))
    for folder in ("findings", "submissions"):
        srcs += list((ROOT / folder).rglob("sound_asset*.txt"))
    tails, stems = collections.Counter(), set()
    for p in srcs:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            k, sep, v = line.partition(",")
            m = R.match((v if sep else k).strip().lower())
            if m:
                stems.add(m.group(1))
                tails[m.group(2)] += 1
    top = [t for t, _ in tails.most_common(40)]
    for s in sorted(stems):
        spellings = {s, s.replace("/", ".")} if a.dotted else {s}
        for sp in spellings:
            for t in top:
                print(sp + t)
    print(f"{len(stems):,} stems x {len(top)} tails", file=sys.stderr)


if __name__ == "__main__":
    main()
