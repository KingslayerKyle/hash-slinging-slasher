"""Complete BO4 image channels written immediately before a retained tail.

``image_channels.py`` rewrites an image's final channel suffix, and ``--deep``
cuts two final tokens before adding a new suffix.  Neither can turn an attested
``..._c_01`` spelling into ``..._n_01``: the channel is in place and the
numbered/size tail must remain byte-for-byte intact.

This is deliberately not a generic token substitution.  For each one- or
two-token tail layout, it first requires at least ``--min-controls`` distinct
same-core image groups that already carry two channels.  It then offers only
the channels actually observed with that exact retained-tail layout.  Thus
both the position and every surrounding byte are measured from BO4-era image
names; no channel, tail, or stem is invented.
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


# The normal channel derivation's measured vocabulary.  This deliberately
# shares it rather than inventing an image decoration from a bare word.
CHANNELS = frozenset((
    "c", "n", "g", "o", "m", "s", "r", "e", "col", "nml", "icon",
    "large", "spc", "gls", "ao", "d", "h", "a", "mask", "small",
))


def corpus():
    names = set(snapshot.table_names("fnv1a_ximages"))
    names.update(snapshot.confirmed_names("image"))
    return {
        name.strip().lower().replace("\\", "/")
        for name in names
        if name.strip() and len(name) <= 240
    }


def parsed_groups(names):
    """Map a complete in-place frame to its attested channel spellings."""
    groups = collections.defaultdict(set)
    for name in names:
        directory, marker, base = name.rpartition("/")
        directory = directory + marker if marker else ""
        if "." in base:
            continue
        tokens = tuple(token for token in base.split("_") if token)
        # A retained tail must be real tokens, never a directory or extension.
        for tail_width in (1, 2):
            if len(tokens) <= tail_width + 1:
                continue
            at = len(tokens) - tail_width - 1
            channel = tokens[at]
            if channel not in CHANNELS:
                continue
            prefix = tokens[:at]
            tail = tokens[at + 1 :]
            groups[(directory, prefix, tail)].add(channel)
    return groups


def derive(groups, known, minimum):
    # A tail style is admitted only after many independent exact-core sibling
    # controls.  Its channel palette is also learned separately, so a channel
    # that belongs to ``_c_01`` is never assumed for ``_c_large``.
    controls = collections.Counter()
    palettes = collections.defaultdict(set)
    for (_, _, tail), channels in groups.items():
        palettes[tail].update(channels)
        if len(channels) >= 2:
            controls[tail] += 1
    eligible = {tail for tail, count in controls.items() if count >= minimum}

    output = set()
    for (directory, prefix, tail), channels in groups.items():
        if tail not in eligible:
            continue
        for channel in palettes[tail] - channels:
            output.add(directory + "_".join(prefix + (channel,) + tail))
    return output - known, controls, palettes, eligible


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-controls", type=int, default=25)
    parser.add_argument("--count", action="store_true")
    options = parser.parse_args(argv)
    if options.min_controls < 1:
        raise SystemExit("--min-controls must be positive")

    known = corpus()
    groups = parsed_groups(known)
    output, controls, palettes, eligible = derive(groups, known, options.min_controls)
    complete = sum(controls.values())
    print(
        f"{len(known):,} known images; {len(groups):,} in-place channel frames; "
        f"{complete:,} complete same-core controls across {len(controls):,} retained tails; "
        f"{len(eligible):,} tail layouts at {options.min_controls}+ controls; "
        f"{len(output):,} unseen candidates",
        file=sys.stderr,
    )
    if not options.count:
        print("\n".join(sorted(output)))


if __name__ == "__main__":
    main(sys.argv[1:])
