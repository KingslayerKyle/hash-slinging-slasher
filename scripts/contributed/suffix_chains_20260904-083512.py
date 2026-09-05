"""Extend a real name by a suffix only where the exact chain has real controls.

Run:
    python contrib/suffix_chains_20260904.py --measure
    python contrib/suffix_chains_20260904.py | target\\release\\confirm_list.exe - --game BLKOPS04 --label "controlled suffix chains" --script contrib/suffix_chains_20260904.py

Reads the published tables, locally confirmed names, and data/suffixes.txt.  It writes candidate
names to stdout, one per line.  This is reusable: each candidate is a real spelling ending in A
with B appended, but (A, B) is retained only when another real spelling proves that exact step.
"""
import argparse
import collections
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
while ROOT != os.path.dirname(ROOT) and not os.path.isfile(
    os.path.join(ROOT, "scripts", "snapshot.py")
):
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import snapshot


TABLES = (
    "fnv1a_xmodels",
    "fnv1a_xmaterials",
    "fnv1a_ximages",
    "fnv1a_xanims",
    "fnv1a_soundbanks_aliases",
)


def known_names():
    names = set()
    for table in TABLES:
        names.update(snapshot.table_names(table))
    names.update(snapshot.confirmed_names())
    return {name.strip().lower().replace("\\\\", "/") for name in names if name.strip()}


def endings(names, limit):
    # Count suffixes as the list builder does: an ending is one trailing underscore segment.
    counts = collections.Counter(
        "_" + name.rsplit("_", 1)[1]
        for name in names
        if "_" in name and len(name.rsplit("_", 1)[1]) >= 1
    )
    listed = {
        line.strip()
        for line in open(os.path.join(ROOT, "data", "suffixes.txt"), encoding="utf-8")
        if line.strip()
    }
    # The current list is the actual general-search vocabulary.  A chain already represented by
    # it is not new reach, however often it occurs in the corpus.
    atoms = [ending for ending, _ in counts.most_common(limit)]
    return atoms, listed


def controlled_pairs(names, atoms, listed):
    pairs = collections.Counter()
    for whole in names:
        for tail in atoms:
            if not whole.endswith(tail):
                continue
            base = whole[: -len(tail)]
            if base not in names or "_" not in base:
                continue
            first = "_" + base.rsplit("_", 1)[1]
            if first not in atoms:
                continue
            joined = first + tail
            if joined not in listed:
                pairs[(first, tail)] += 1
    return pairs


def candidates(names, by_first):
    for first, tails in sorted(by_first.items()):
        for name in sorted(names):
            if name.endswith(first):
                for tail in tails:
                    yield name + tail


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--limit", type=int, default=50, help="common ending atoms to consider")
    parser.add_argument("--measure", action="store_true", help="report controls without candidates")
    options = parser.parse_args(argv)

    names = known_names()
    atoms, listed = endings(names, options.limit)
    pairs = controlled_pairs(names, atoms, listed)
    by_first = collections.defaultdict(list)
    for (first, tail), controls in pairs.items():
        by_first[first].append(tail)
    candidate_count = sum(
        sum(1 for name in names if name.endswith(first)) * len(tails)
        for first, tails in by_first.items()
    )
    print(
        "known names: {:,}; atoms: {}; controlled omitted chains: {}; controls: {:,}; candidates: {:,}".format(
            len(names), len(atoms), len(pairs), sum(pairs.values()), candidate_count
        ),
        file=sys.stderr,
    )
    for (first, tail), controls in pairs.most_common():
        print("  {} + {}: {:,} controls".format(first, tail, controls), file=sys.stderr)
    if options.measure:
        return 0
    for name in candidates(names, by_first):
        print(name)


if __name__ == "__main__":
    result = main(sys.argv[1:])
    if result is not None:
        sys.exit(result)
