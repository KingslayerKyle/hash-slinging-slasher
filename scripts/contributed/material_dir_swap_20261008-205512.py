"""Modern material bases crossed with every material directory, plus image stems as bases.

A modern material is `<dir>/<base>` -- `tm/`, `m/`, `tmo/`, `tm7/`, `i/`, `elcq/` and about forty
more, measured off the published `_v2` table. The directory is a technique/usage class rather
than part of the name, so a base proven under one directory is a candidate under every other one,
and an image's stem (channel suffix `_c`/`_n`/`_g`/`_s`... removed) is a candidate base too: `i/`
materials are named straight off their image. `twc/` is left out as a base source: those are
numeric terrain-blend grids, handled by contrib/twc_*.plan.txt.

    python contrib/material_dir_swap.py | confirm_list - --game BLACKOP6 --script contrib/material_dir_swap.py
"""
from pathlib import Path
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

CHANNEL = re.compile(r"_(c|n|g|s|o|e|a|r|m|h|nog|col|nml|gls|spc|occ|mask|alpha|d)$")


def rows(table_glob, kinds):
    for f in sorted((ROOT / "cod-name-db" / "csv").glob(table_glob)):
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "submissions", "findings", "contrib/open_pr_names"):
        for kind in kinds:
            for f in sorted((ROOT / top).rglob(kind + "*.txt")):
                for line in f.open(encoding="utf-8", errors="replace"):
                    key, sep, name = line.rstrip("\r\n").partition(",")
                    if sep:
                        yield name.lower()


def main():
    dirs = collections.Counter()
    bases = set()
    for name in rows("fnv1a_xmaterials*.csv", ("material",)):
        d, sep, base = name.partition("/")
        if not sep or not base:
            continue
        dirs[d] += 1
        if d != "twc" and not base.startswith("*"):
            bases.add(base)
    for name in rows("fnv1a_ximages*.csv", ("image",)):
        if "&" in name or "~" in name or "/" in name:
            continue
        bases.add(name)
        m = CHANNEL.search(name)
        if m:
            bases.add(name[: m.start()])
    top = [d for d, n in dirs.most_common() if n >= 20 and d != "twc"]
    print(f"{len(bases)} bases x {len(top)} dirs", file=sys.stderr)
    out = sys.stdout
    for base in sorted(bases):
        out.write("".join(f"{d}/{base}\n" for d in top))


if __name__ == "__main__":
    main()
