"""Modern image channel completion, including the parts of packed images.

Modern titles publish two image shapes in `fnv1a_ximages_v2`: plain names
(`wpn_p44_sh_tsierra12_upper_v0_cm`) and packed ones (`A_c&A_s~<64-bit decimal>`), where the
decimal suffix is not an FNV hash of the text or of the parts' ids (measured 2026-10-09: 0 of 300
under either basis, either mask, xor/add/mul/concat/chain) and so cannot be rebuilt. The parts of a
packed name are image names in their own right, though, so each part is offered as is, and every
core -- a plain name or a part, cut at its final `_<channel>` -- is offered under every channel
modern images are measured to use.

Spent by: the image corpus as it stands; re-run after new images are confirmed in any game.
"""
from collections import Counter
from pathlib import Path
import argparse
import re
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
CHANNEL = re.compile(r"^(.+)_([a-z]{1,4}\d?)$")


def names():
    sources = [ROOT / "cod-name-db" / "csv" / "fnv1a_ximages_v2.csv",
               ROOT / "cod-name-db" / "csv" / "fnv1a_ximages.csv"]
    for folder in ("submissions", "findings", "all_names"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("image*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower()
            if name:
                yield name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--channels", type=int, default=40, help="most common channel suffixes to offer")
    args = ap.parse_args()

    parts, cores, channels = set(), set(), Counter()
    for name in names():
        pieces = name.rpartition("~")[0].split("&") if "~" in name else [name]
        for piece in pieces:
            parts.add(piece)
            m = CHANNEL.match(piece)
            if m:
                cores.add(m.group(1))
                channels[m.group(2)] += 1

    offered = [c for c, _ in channels.most_common(args.channels)]
    seen = set()
    for piece in sorted(parts):
        if piece not in seen:
            seen.add(piece)
            print(piece)
    for core in sorted(cores):
        for ch in offered:
            candidate = f"{core}_{ch}"
            if candidate not in seen:
                print(candidate)
    print(f"{len(parts):,} parts, {len(cores):,} cores x {len(offered)} channels: {' '.join(offered)}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
