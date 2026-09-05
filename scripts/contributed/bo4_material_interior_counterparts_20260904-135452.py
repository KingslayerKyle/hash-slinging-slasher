"""Offer strongly attested BO4 material-token counterparts at an interior position.

This is the material-only counterpart to the BO4 image whole-frame relation.
It retains the directory, token position, and every other basename token.  A
replacement is allowed only after its unordered pair occurs in at least 200
independent complete material frames.  One-character grid states and the NATO
alphabet are deliberately excluded: their combinatorics are not a naming
convention and would turn this into a state sweep.
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


# These observed groups are numbering/state alphabets rather than material
# words.  Excluding the whole alphabet rather than merely a few pairs keeps
# the candidate set a counterpart relation, not an implicit grid generator.
GRID_TOKENS = frozenset((
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "alfa", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliett", "kilo", "lima", "mike", "november",
))


def corpus():
    names = set(snapshot.table_names("fnv1a_xmaterials"))
    names.update(snapshot.confirmed_names("material"))
    return {
        name.strip().lower().replace("\\", "/")
        for name in names
        if name.strip() and len(name) <= 240
    }


def frames(names):
    """Map an exact material spelling with one interior word removed to words."""
    out = collections.defaultdict(set)
    for name in names:
        directory, marker, basename = name.rpartition("/")
        directory = directory + marker if marker else ""
        if "." in basename:
            continue
        tokens = tuple(basename.split("_"))
        if len(tokens) < 4 or any(not token for token in tokens):
            continue
        for index in range(1, len(tokens) - 1):
            token = tokens[index]
            if not token.isalpha() or token in GRID_TOKENS:
                continue
            out[(directory, index, tokens[:index], tokens[index + 1:])].add(token)
    return out


def derive(grouped, known, minimum):
    controls = collections.Counter()
    for values in grouped.values():
        values = sorted(values)
        for index, left in enumerate(values):
            for right in values[index + 1:]:
                controls[(left, right)] += 1
    eligible = {pair for pair, count in controls.items() if count >= minimum}
    counterparts = collections.defaultdict(set)
    for left, right in eligible:
        counterparts[left].add(right)
        counterparts[right].add(left)

    output = set()
    for (directory, _, head, tail), values in grouped.items():
        for value in values:
            for other in counterparts[value]:
                if other not in values:
                    output.add(directory + "_".join(head + (other,) + tail))
    return output - known, controls, eligible


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--min-controls", type=int, default=200)
    parser.add_argument("--count", action="store_true")
    options = parser.parse_args(argv)
    if options.min_controls < 1:
        raise SystemExit("--min-controls must be positive")
    known = corpus()
    grouped = frames(known)
    output, controls, eligible = derive(grouped, known, options.min_controls)
    print(
        f"{len(known):,} known materials; {len(grouped):,} exact interior frames; "
        f"{len(eligible):,} pairs at {options.min_controls:,}+ complete-frame controls; "
        f"{sum(controls[pair] for pair in eligible):,} controls; "
        f"{len(output):,} unseen candidates",
        file=sys.stderr,
    )
    if not options.count:
        print("\n".join(sorted(output)))


if __name__ == "__main__":
    main(sys.argv[1:])
