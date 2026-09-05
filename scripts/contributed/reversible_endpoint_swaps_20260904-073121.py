"""Swap endpoints around an unchanged token only for observed reversible triples.

For an interior ``left_middle_right`` triple, emit ``right_middle_left`` only
when that reverse triple occurs in a real name somewhere in the corpus.  The
directory and every other token stay fixed.  This is a distance-two, in-place
relation, not an adjacent-token permutation or fragment recombination.
"""

from pathlib import Path
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
    if len(tokens) < 3 or any(not token for token in tokens):
        return None
    return (directory + marker if marker else ""), tokens


def main() -> None:
    known = corpus()
    parsed = [item for name in known if (item := split(name))]
    triples = {
        (tokens[index - 1], tokens[index], tokens[index + 1])
        for _, tokens in parsed
        for index in range(1, len(tokens) - 1)
    }
    reversible = {
        triple
        for triple in triples
        if (triple[2], triple[1], triple[0]) in triples and triple[0] != triple[2]
    }
    output: set[str] = set()
    controls = 0
    for directory, tokens in parsed:
        for index in range(1, len(tokens) - 1):
            triple = (tokens[index - 1], tokens[index], tokens[index + 1])
            if triple not in reversible:
                continue
            changed = list(tokens)
            changed[index - 1], changed[index + 1] = changed[index + 1], changed[index - 1]
            candidate = directory + "_".join(changed)
            if candidate in known:
                controls += 1
            else:
                output.add(candidate)
    print(
        f"{len(known):,} known names; {len(reversible):,} reversible triples; "
        f"{controls:,} full-name controls; {len(output):,} unseen candidates",
        file=sys.stderr,
    )
    print("\n".join(sorted(output)))


if __name__ == "__main__":
    main()
