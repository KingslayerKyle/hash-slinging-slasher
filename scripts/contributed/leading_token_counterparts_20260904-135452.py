"""Controlled leading-basename-token counterparts.

This is the leading-position mirror of the recent whole-frame interior-token
relation.  It never changes a directory, tail, channel, numeric tag, or the
number of tokens: only the first *alphabetic* basename token can change, and
only if the exact retained frame has established that counterpart pairing many
times in independently known names.  Middle substitutions, terminal roles,
and token edits therefore do not subsume it.
"""
import argparse
import collections
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims")
WORD = re.compile(r"^[a-z]+$")
MAX_CHOICES = 8
EXCLUDED = {("i", "mtl"), ("mtl", "sub")}


def corpus():
    names = set(snapshot.table_names(*TABLES))
    for kind in ("xmodel", "material", "image", "xanim"):
        names.update(snapshot.confirmed_names(kind))
    return {n.strip().lower().replace("\\\\", "/") for n in names if n.strip() and len(n) <= 240}


def split(name):
    directory, slash, base = name.rpartition("/")
    first, sep, tail = base.partition("_")
    if not slash or not sep or not tail or not WORD.fullmatch(first):
        return None
    return directory + slash, first, tail


def build(known, minimum, maximum):
    frames = collections.defaultdict(set)
    for name in known:
        parsed = split(name)
        if parsed:
            directory, first, tail = parsed
            frames[(directory, tail)].add(first)
    frames = {frame: choices for frame, choices in frames.items() if len(choices) <= MAX_CHOICES}
    controls = collections.Counter()
    for choices in frames.values():
        for left in choices:
            for right in choices:
                if left < right:
                    controls[(left, right)] += 1
    # i<->mtl is the already-closed material/image seam, while mtl<->sub is
    # its material-prefix analogue.  Both generate a broad prefix sweep, not
    # a new counterpart convention, so their known controls are excluded.
    eligible = {
        pair for pair, count in controls.items()
        if minimum <= count <= maximum and pair not in EXCLUDED
    }
    alternatives = collections.defaultdict(set)
    for left, right in eligible:
        alternatives[left].add(right)
        alternatives[right].add(left)
    out = set()
    for (directory, tail), choices in frames.items():
        for first in choices:
            for other in alternatives[first]:
                if other not in choices:
                    out.add(directory + other + "_" + tail)
    return out - known, len(eligible), sum(controls[p] for p in eligible)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", action="store_true")
    parser.add_argument("--min-controls", type=int, default=100)
    parser.add_argument("--max-controls", type=int, default=1000)
    options = parser.parse_args()
    known = corpus()
    out, pairs, controls = build(known, options.min_controls, options.max_controls)
    print(f"{len(known):,} non-sound names; {pairs:,} eligible leading pairs at {options.min_controls:,}..{options.max_controls:,} controls; {controls:,} exact-frame controls; {len(out):,} unseen candidates", file=sys.stderr)
    if not options.count:
        print("\n".join(sorted(out)))


if __name__ == "__main__":
    main()
