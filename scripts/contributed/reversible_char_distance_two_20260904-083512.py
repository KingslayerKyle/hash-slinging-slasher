"""Reverse two characters around a fixed middle character only when attested.

Within one non-dotted basename token, ``abc`` may become ``cba`` only if both
trigrams recur at least twenty times in real tokens.  The rest of the token,
basename, and directory is unchanged.  This is distinct from adjacent-character
transposition and is deliberately gated by observed spelling evidence.
"""

from collections import Counter
from pathlib import Path
import argparse
import sys


ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "scripts"))
import snapshot


TABLES = (
    "fnv1a_xmodels",
    "fnv1a_xmaterials",
    "fnv1a_ximages",
    "fnv1a_xanims",
    "fnv1a_soundbanks_aliases",
)
MIN_OCCURRENCES = 20


def corpus() -> set[str]:
    names = set(snapshot.table_names(*TABLES))
    names.update(snapshot.confirmed_names())
    return {
        name.strip().lower().replace("\\", "/")
        for name in names
        if name.strip() and len(name) <= 240
    }


def split(name: str) -> tuple[str, list[str]] | None:
    directory, marker, basename = name.rpartition("/")
    if "." in basename:
        return None
    tokens = basename.split("_")
    if any(not token for token in tokens):
        return None
    return (directory + marker if marker else ""), tokens


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", action="store_true")
    options = parser.parse_args()
    known = corpus()
    parsed = [item for name in known if (item := split(name))]
    counts = Counter(
        token[index : index + 3]
        for _, tokens in parsed
        for token in tokens
        for index in range(len(token) - 2)
    )
    reversible = {
        trigram
        for trigram, count in counts.items()
        if count >= MIN_OCCURRENCES
        and counts[trigram[::-1]] >= MIN_OCCURRENCES
        and trigram[0] != trigram[2]
    }
    output: set[str] = set()
    controls = 0
    for directory, tokens in parsed:
        for token_index, token in enumerate(tokens):
            for index in range(len(token) - 2):
                trigram = token[index : index + 3]
                if trigram not in reversible:
                    continue
                changed_token = token[:index] + trigram[::-1] + token[index + 3 :]
                changed = list(tokens)
                changed[token_index] = changed_token
                candidate = directory + "_".join(changed)
                if candidate in known:
                    controls += 1
                else:
                    output.add(candidate)
    print(
        f"{len(known):,} known names; {len(reversible):,} reversible character trigrams; "
        f"{controls:,} full-name controls; {len(output):,} unseen candidates",
        file=sys.stderr,
    )
    if not options.count:
        print("\n".join(sorted(output)))


if __name__ == "__main__":
    main()
