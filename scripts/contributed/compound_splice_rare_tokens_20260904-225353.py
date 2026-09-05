"""Generate rare-token compound splices from independently observed name halves.

    python contrib/compound_splice_rare_tokens.py > candidates.txt

Reads the published and confirmed names through ``scripts/snapshot.py`` and writes candidate
asset names to stdout; it writes no repository files.  This is a reusable bounded experiment:
only tokens occurring in 2--20 names are used, and each candidate joins a prefix and suffix from
different observed names at that shared token.
"""
import collections
import os
import sys

_root = os.path.dirname(os.path.abspath(__file__))
while _root != os.path.dirname(_root) and not os.path.isfile(os.path.join(_root, "scripts", "snapshot.py")):
    _root = os.path.dirname(_root)
sys.path.insert(0, os.path.join(_root, "scripts"))
import snapshot

TABLES = ("fnv1a_xmodels", "fnv1a_xmaterials", "fnv1a_ximages", "fnv1a_xanims", "fnv1a_soundbanks_aliases")
MIN_TOKEN_NAMES = 2
MAX_TOKEN_NAMES = 20


def names():
    values = []
    for table in TABLES:
        values.extend(snapshot.table_names(table))
    values.extend(snapshot.confirmed_names())
    return {x.strip().lower().replace("\\", "/") for x in values if x.strip()}


def split(value):
    directory, sep, rest = value.partition("/")
    if sep and len(directory) <= 6 and "_" not in directory:
        return directory + "/", rest.split("_")
    return "", value.split("_")


def main():
    corpus = names()
    occurrences = collections.Counter()
    halves = collections.defaultdict(lambda: {"prefix": set(), "suffix": set()})
    for value in corpus:
        directory, parts = split(value)
        if len(parts) < 4:
            continue
        for i, token in enumerate(parts[1:-1], 1):
            occurrences[token] += 1
            halves[(directory, token)]["prefix"].add("_".join(parts[:i]))
            halves[(directory, token)]["suffix"].add("_".join(parts[i + 1:]))

    candidates = set()
    for (directory, token), sides in halves.items():
        count = occurrences[token]
        if not MIN_TOKEN_NAMES <= count <= MAX_TOKEN_NAMES:
            continue
        for prefix in sides["prefix"]:
            for suffix in sides["suffix"]:
                candidates.add(directory + prefix + "_" + token + "_" + suffix)

    for candidate in sorted(candidates):
        print(candidate)
    print("%s names, %s rare-token candidates" % (len(corpus), len(candidates)), file=sys.stderr)


if __name__ == "__main__":
    main()
