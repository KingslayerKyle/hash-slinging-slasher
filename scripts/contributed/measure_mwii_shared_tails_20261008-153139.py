"""Where does an MWII sound name actually repeat? Measured, so the next plan aims somewhere real.

A blanket `directory x basename x tail` product is weak here, and the reason is visible in one
number: MWII's own corpus holds **44,077 distinct basenames across 45,049 names**, so a basename is
almost unique to its name and crossing it against 1,906 directories asks 482M pairs to reach the
~253k real ones. That is why the whole product found nothing in its first 345 billion candidates.

The repetition that does exist is in the *trailing* tokens: `_fire_plr_shot_03`,
`_reload_empty_fast_magout`, `_inspect_xmaglrg_magrelease` recur across every weapon directory. So
the productive split is `directory + head` against a *shared tail*, where the tail vocabulary is
measured by how many directories each candidate tail actually appears in.

Prints the tail vocabulary at each support threshold, and what a head x tail product would cost.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import settings
import snapshot

TAIL = re.compile(r"\.(?P<chan>[a-z]{1,4})\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")
VARIANT = re.compile(r"_\d+$")


def main():
    game = settings.game()
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_asset", set())

    # tail -> the set of directories it is attested in, and how often.
    support = collections.defaultdict(set)
    counts = collections.Counter()
    heads = collections.Counter()
    total = 0

    for line in (Path(settings.tables_csv()) / "fnv1a_xsounds_v2.csv").open(encoding="utf-8"):
        key, sep, display = line.strip().partition(",")
        if not sep:
            continue
        try:
            key = int(key, 16)
        except ValueError:
            continue
        if key & snapshot.ID_MASK not in ids:
            continue
        restored = snapshot.verified_database_row("fnv1a_xsounds_v2", key, display)
        if restored is None:
            continue
        _, name = restored
        match = TAIL.search(name)
        if not match:
            continue
        head_name = name[: match.start()]
        directory, _, basename = head_name.rpartition(".")
        if not directory:
            continue
        directory += "."
        encoding = name[match.start():]
        core = VARIANT.sub("", basename)
        total += 1

        tokens = core.split("_")
        # Every underscore boundary inside the basename is a possible head/tail cut.
        for cut in range(1, len(tokens)):
            head = directory + "_".join(tokens[:cut])
            tail = "_".join(tokens[cut:])
            if not tail:
                continue
            support[tail].add(directory)
            counts[tail] += 1
            heads[head] += 1

    print("MWII sound names decomposed : %s" % format(total, ","))
    print("distinct head cuts          : %s" % format(len(heads), ","))
    print()
    for threshold in (2, 3, 5, 10, 25, 50):
        kept = [t for t, dirs in support.items() if len(dirs) >= threshold]
        product = len(heads) * len(kept)
        print("tails attested in >= %3d directories : %s tails, head x tail = %s candidates"
              % (threshold, format(len(kept), ","), format(product, ",")))
    print()
    print("strongest shared tails (most directories):")
    for tail, dirs in sorted(support.items(), key=lambda kv: -len(kv[1]))[:25]:
        print("  %-46s %4d directories, %5d uses" % (tail, len(dirs), counts[tail]))


if __name__ == "__main__":
    main()