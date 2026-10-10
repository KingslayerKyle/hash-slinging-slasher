"""Image cores crossed with the long channel suffixes the short-channel scripts cannot express.

`modern_image_channels.py` only cuts a one-to-four-letter `_<channel>`, so suffixes like
`_thermalmap` (18,286 published modern images), `_m0_v2`, `_v0_cm`, `_blueprint_swatch` or
`_preview_flipbook` are never varied. This measures the commonest one- and two-token image suffixes
that are longer than a short channel (or span two tokens), cuts every known image -- plain names and
the parts of packed `A&B~N` names -- at whichever of them it ends with, and offers each core under all
of them. The same idea found 348 new BLACKOP7 images in a parallel worker (its `long_channel_grid`).

Spent by: the image corpus as it stands; re-run after new images are confirmed.
"""
from collections import Counter
from pathlib import Path
import argparse
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')


def names():
    sources = list((ROOT / "cod-name-db" / "csv").glob("fnv1a_ximages*.csv"))
    for folder in ("submissions", "findings", "all_names"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob("image*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower()
            if not name:
                continue
            for piece in (name.rpartition("~")[0].split("&") if "~" in name else [name]):
                if piece:
                    yield piece


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suffixes", type=int, default=120)
    args = ap.parse_args()
    pieces = set(names())
    counted = Counter()
    for p in pieces:
        t = p.split("_")
        if len(t) > 2:
            counted[t[-1]] += 1
            counted["_".join(t[-2:])] += 1
    suffixes = [s for s, _ in counted.most_common(4000)
                if (len(s) > 4 or "_" in s) and not s.replace("_", "").isdigit()][:args.suffixes]
    ordered = sorted(suffixes, key=len, reverse=True)
    cores = set()
    for p in pieces:
        for s in ordered:
            if p.endswith("_" + s):
                cores.add(p[: -len(s) - 1])
                break
    emitted = 0
    for core in sorted(cores):
        for s in suffixes:
            candidate = f"{core}_{s}"
            if candidate not in pieces:
                print(candidate)
                emitted += 1
    print(f"{len(cores):,} cores x {len(suffixes)} long suffixes -> {emitted:,}", file=sys.stderr)


if __name__ == "__main__":
    main()
