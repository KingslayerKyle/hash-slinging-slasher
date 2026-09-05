"""Swap adjacent middle tokens only for token orders proven by whole-name controls.

Run:
    python contrib/adjacent_middle_token_swap_20260904.py --measure
    python contrib/adjacent_middle_token_swap_20260904.py | target\\release\\confirm_list.exe - --game BLKOPS04 --label "controlled adjacent middle token swaps" --script contrib/adjacent_middle_token_swap_20260904.py

Reads the published tables and confirmed names, and writes candidate names to stdout.  Reusable:
this deliberately excludes endpoint swaps (a separate, already measured method) and accepts an
ordered token pair only after at least five complete real names reproduce under that exact swap.
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


def swaps(name):
    # A slash remains attached to the first token and dots are left alone: neither is an
    # underscore-token ordering convention.  Endpoints are intentionally excluded.
    if "." in name:
        return
    tokens = name.split("_")
    if len(tokens) < 4:
        return
    for index in range(1, len(tokens) - 2):
        changed = tokens.copy()
        changed[index], changed[index + 1] = changed[index + 1], changed[index]
        yield (tokens[index], tokens[index + 1]), "_".join(changed)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--minimum", type=int, default=5, help="whole-name controls per ordered pair")
    parser.add_argument("--measure", action="store_true", help="report controls without candidates")
    options = parser.parse_args(argv)

    names = known_names()
    controls = collections.Counter()
    for name in names:
        for pair, changed in swaps(name) or ():
            if changed in names:
                controls[pair] += 1
    eligible = {pair for pair, count in controls.items() if count >= options.minimum}
    candidates = set()
    for name in names:
        for pair, changed in swaps(name) or ():
            if pair in eligible and changed not in names:
                candidates.add(changed)

    print(
        "known names: {:,}; directed pairs with controls: {:,}; eligible at {}: {:,}; "
        "whole-name controls: {:,}; unseen candidates: {:,}".format(
            len(names), len(controls), options.minimum, len(eligible),
            sum(controls[pair] for pair in eligible), len(candidates)
        ),
        file=sys.stderr,
    )
    for pair, count in controls.most_common(30):
        if pair in eligible:
            print("  {} <-> {}: {:,} controls".format(pair[0], pair[1], count), file=sys.stderr)
    if not options.measure:
        for candidate in sorted(candidates):
            print(candidate)


if __name__ == "__main__":
    main(sys.argv[1:])
