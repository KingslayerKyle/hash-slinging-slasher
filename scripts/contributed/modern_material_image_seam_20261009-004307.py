"""Modern materials and images named from each other's cores.

A modern material is `<dir>/<core>` (`m/`, `tm/`, `tm7/`, `mo/`, `i/`, ...; `twc/` and `tw/` are
numeric packing codes and are skipped), and its textures are very often `<core>_<channel>` images.
This offers, both ways:

* every image core (an image name cut at its final `_<channel>`, plain or a part of a packed
  `A&B~N` name) under every measured material directory, and
* every material core under every measured image channel.

Directories and channels are the most common ones measured from the v2 tables.

Spent by: the material and image corpora as they stand; re-run after either grows.
"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = next((p for p in Path(__file__).resolve().parents
             if (p / 'scripts/snapshot.py').is_file()), None)
if ROOT is None:
    raise SystemExit('Run this generator from a solver checkout')
CHANNEL = re.compile(r"^(.+)_([a-z]{1,4}\d?)$")
SKIP_DIRS = {"twc", "tw", "twcj"}


def rows(glob, kind):
    sources = list((ROOT / "cod-name-db" / "csv").glob(glob))
    for folder in ("submissions", "findings"):
        base = ROOT / folder
        if base.exists():
            sources.extend(base.rglob(kind + "*.txt"))
    for path in sources:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            key, sep, value = line.partition(",")
            name = (value if sep else key).strip().lower()
            if name:
                yield name


def main():
    dirs, mat_cores = Counter(), set()
    for name in rows("fnv1a_xmaterials*.csv", "material"):
        if "/" in name:
            d, _, core = name.partition("/")
            if d in SKIP_DIRS or core.startswith("*"):
                continue
            dirs[d] += 1
            mat_cores.add(core)
    channels, img_cores = Counter(), set()
    for name in rows("fnv1a_ximages*.csv", "image"):
        pieces = name.rpartition("~")[0].split("&") if "~" in name else [name]
        for piece in pieces:
            m = CHANNEL.match(piece)
            if m:
                img_cores.add(m.group(1))
                channels[m.group(2)] += 1

    top_dirs = [d for d, _ in dirs.most_common(16)]
    top_ch = [c for c, _ in channels.most_common(12)]
    seen = 0
    for core in sorted(img_cores - mat_cores):
        for d in top_dirs:
            print(f"{d}/{core}")
            seen += 1
    for core in sorted(mat_cores):
        for c in top_ch:
            print(f"{core}_{c}")
            seen += 1
    print(f"{seen:,} candidates; dirs {' '.join(top_dirs)}; channels {' '.join(top_ch)}", file=sys.stderr)


if __name__ == "__main__":
    main()
