"""Offer strongly attested image-token counterparts at an interior position.

Run: ``python contrib/bo4_image_interior_counterparts_20260904.py | target\\release\\confirm_list.exe - --game BLKOPS04 --label \"BO4 image interior counterparts\" --script contrib/bo4_image_interior_counterparts_20260904.py``.
Reads the BO4-era ximage table plus confirmed image names through snapshot.py and writes one
candidate per line to stdout.  Reusable: it measures its controls again after a new image seed.

Unlike slotswap, this keeps an entire image spelling fixed apart from one *interior* alphabetic
token.  A token pair is offered only after that exact pair has occurred in at least N independent
complete frames (directory, every other basename token, and token position all retained).  This
is deliberately narrower than generic substitution and excludes image channel positions, which
the channel derivations own.
"""

import argparse
import collections
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import snapshot


CHANNELS = frozenset((
    "c", "n", "g", "o", "m", "s", "r", "e", "col", "nml", "icon",
    "large", "spc", "gls", "ao", "d", "h", "a", "mask", "small",
))


def corpus():
    names = set(snapshot.table_names("fnv1a_ximages"))
    names.update(snapshot.confirmed_names("image"))
    return {
        name.strip().lower().replace("\\\\", "/")
        for name in names
        if name.strip() and len(name) <= 240
    }


def parsed(names):
    """Yield (directory, tokens), excluding dots and malformed basenames."""
    for name in names:
        directory, mark, basename = name.rpartition("/")
        if "." in basename:
            continue
        tokens = tuple(basename.split("_"))
        if len(tokens) < 4 or any(not token for token in tokens):
            continue
        yield directory + mark if mark else "", tokens


def measure(known, minimum):
    # A complete frame is the exact spelling with one token omitted.  Requiring
    # a pair in many such frames is evidence that it is a real interchangeable
    # image-role spelling, not merely two words sharing local neighbours.
    frames = collections.defaultdict(set)
    for directory, tokens in parsed(known):
        for index in range(1, len(tokens) - 1):
            token = tokens[index]
            if not token.isalpha() or token in CHANNELS:
                continue
            frame = (directory, index, tokens[:index], tokens[index + 1:])
            frames[frame].add(token)

    controls = collections.Counter()
    for values in frames.values():
        if len(values) < 2:
            continue
        ordered = sorted(values)
        for left_index, left in enumerate(ordered):
            for right in ordered[left_index + 1:]:
                controls[(left, right)] += 1
    eligible = {pair for pair, count in controls.items() if count >= minimum}

    counterparts = collections.defaultdict(set)
    for left, right in eligible:
        counterparts[left].add(right)
        counterparts[right].add(left)

    output = set()
    for (directory, index, head, tail), values in frames.items():
        for value in values:
            for other in counterparts[value]:
                if other not in values:
                    output.add(directory + "_".join(head + (other,) + tail))
    return output - known, len(frames), controls, eligible


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-controls", type=int, default=50)
    parser.add_argument("--count", action="store_true")
    options = parser.parse_args(argv)
    if options.min_controls < 1:
        raise SystemExit("--min-controls must be positive")
    known = corpus()
    output, frame_count, controls, eligible = measure(known, options.min_controls)
    print(
        f"{len(known):,} known images; {frame_count:,} interior frames; "
        f"{len(eligible):,} token pairs at {options.min_controls:,}+ complete-frame controls; "
        f"{sum(controls[pair] for pair in eligible):,} controls; {len(output):,} unseen candidates",
        file=sys.stderr,
    )
    if not options.count:
        print("\n".join(sorted(output)))


if __name__ == "__main__":
    main(sys.argv[1:])
