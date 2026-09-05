"""Try previously unseen, well-controlled terminal-token counterpart pairs.

Only alphabetic final underscore tokens are considered.  A pair is eligible only
when at least 20 exact same-base names carry both sides, and the established
prone/stand, L/R, diagonal, left/right, exo1/exo2, and view/world relations are
excluded.  This is deliberately a single census, not a state-grid generator.
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


TABLES = (
    "fnv1a_xmodels",
    "fnv1a_xmaterials",
    "fnv1a_ximages",
    "fnv1a_xanims",
    "fnv1a_xsounds",
    "fnv1a_soundbanks_aliases",
)
TOKEN = re.compile(r"^[a-z]+$")
EXCLUDED = {
    frozenset(("prone", "stand")),
    frozenset(("l", "r")),
    frozenset(("fl", "fr")),
    frozenset(("bl", "br")),
    frozenset(("left", "right")),
    frozenset(("exo1", "exo2")),
    frozenset(("view", "world")),
}
MAX_TOKENS_PER_BASE = 8


def corpus() -> set[str]:
    names = set(snapshot.table_names(*TABLES))
    names.update(snapshot.confirmed_names())
    return {
        name.strip().lower().replace("\\", "/")
        for name in names
        if name.strip() and len(name) <= 240
    }


def split(name: str) -> tuple[str, str] | None:
    base, separator, token = name.rpartition("_")
    if not separator or not base or not TOKEN.fullmatch(token):
        return None
    return base, token


def candidates(known: set[str], minimum_controls: int) -> tuple[set[str], int, int]:
    families: dict[str, set[str]] = collections.defaultdict(set)
    for name in known:
        parsed = split(name)
        if parsed:
            base, token = parsed
            families[base].add(token)

    controls: collections.Counter[frozenset[str]] = collections.Counter()
    # Large terminal sets are state grids; they neither provide a constrained
    # counterpart relation nor justify quadratic pair enumeration.
    families = {
        base: tokens
        for base, tokens in families.items()
        if len(tokens) <= MAX_TOKENS_PER_BASE
    }
    for tokens in families.values():
        for left in tokens:
            for right in tokens:
                if left < right:
                    controls[frozenset((left, right))] += 1

    eligible = {
        pair
        for pair, count in controls.items()
        if count >= minimum_controls and pair not in EXCLUDED
    }
    output: set[str] = set()
    for base, tokens in families.items():
        for pair in eligible:
            left, right = tuple(pair)
            if left in tokens and right not in tokens:
                output.add(f"{base}_{right}")
            elif right in tokens and left not in tokens:
                output.add(f"{base}_{left}")
    return output - known, len(eligible), sum(controls[pair] for pair in eligible)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", action="store_true")
    parser.add_argument("--min-controls", type=int, default=20)
    options = parser.parse_args()
    known = corpus()
    output, pairs, controls = candidates(known, options.min_controls)
    print(
        f"{len(known):,} known names; {pairs:,} eligible terminal pairs at "
        f"{options.min_controls:,}+ controls; "
        f"{controls:,} complete-base controls; {len(output):,} unseen candidates",
        file=sys.stderr,
    )
    if not options.count:
        print("\n".join(sorted(output)))


if __name__ == "__main__":
    main()
