"""Strip Modern Warfare 2019's material directory, so Cold War's can go on instead.

    python contrib/mw19_dir_swap.py --audit    the directory vocabulary, measured
    python contrib/mw19_dir_swap.py            write the bodies

## The observation

CLAUDE.md §6 records that Cold War material names are paths under twelve directories -- `mc/`,
`wc/`, `clt/`, `splm/` and the rest -- and METHODS method 19 added a thirteenth, `mcdp/`. Modern
Warfare 2019's material names are paths too, under *its own* directories. Measured off the
capture rather than assumed:

    twc4/ 134,344   m2o/ 35,991   mo/ 31,295   tm/ 25,262   tmo/ 11,692   mco/ 7,450

That is the same relationship as the channel code. The directory is a fact about the **title**;
the body after it is a fact about the **asset**, and the two titles share assets. So take the
body and let Cold War's own directory go on the front.

Measured 2026-08-23, as a ceiling: **8,790 known Cold War material names are exactly a Cold War
directory plus one of these bodies** -- 1.28% of 688,921. That is the same order as the middles
method, which reached 7.96% and returned 256, and it is over a larger body list (250,604).

## The general shape, which is the point

Three parts of a Modern Warfare 2019 name say which *title* it is rather than which *asset*:

    the directory        twc4/ m2o/ mo/ tm/            -> `mw19_dir_swap.py`
    the channel code     _c _g _n _s _o                -> `mw19_channel_swap.py`
    the version and LOD  _vNN (145,681)  _lodN (137,848)

Strip a title-specific part, put the target title's own back on. Every one of these is the same
idea pointed at a different field, and the third is unbuilt.
"""

import argparse
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").exists() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "scripts"))

import snapshot

# Measured off the capture, commonest first. Not guessed: guessing which punctuation and which
# codes count is what lost the packed-channel names for most of 2026-08-23.
MW19_DIRS = ("twc4/", "m2o/", "tmco/", "tmo/", "mco/", "mo/", "tm/", "vfx/", "i/")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--min-body", type=int, default=8)
    parser.add_argument("--out", default="mw19_dir_bodies.txt")
    args = parser.parse_args()

    seen = collections.Counter()
    bodies = set()
    for _pool, name in snapshot.name_corpus("modwar19"):
        for piece in snapshot.unpack(name.lower()):
            head, sep, rest = piece.partition("/")
            if not sep:
                continue
            seen[head + "/"] += 1
            if (head + "/") in MW19_DIRS and len(rest) >= args.min_body:
                bodies.add(rest)

    if args.audit:
        print("leading directories in the capture, commonest first:\n")
        for directory, count in seen.most_common(20):
            mark = "  <-- carried" if directory in MW19_DIRS else ""
            print(f"  {count:7}  {directory}{mark}")
        print(f"\nbodies that would be written: {len(bodies)}")
        return

    out = ROOT / "contrib" / args.out
    out.write_text("\n".join(sorted(bodies)) + "\n", encoding="utf-8")
    print(f"{len(bodies)} bodies -> contrib/{args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
