"""Measure Modern Warfare II sound-file names as the dot-separated paths they actually are.

`derive_modern_lists.py` splits a name at `/` to find its directory and then at `_` to find its
tokens. MWII sound names carry neither of those at their real boundaries: the path separator is a
period, and the tail is a four-component encoding (`.ln.75.48000.all`). So the carried prefix list
can only ever express a directory that happens to contain no underscore, and it cannot express a
bare directory at all.

This measures the decomposition the naming convention actually implies -- strip the encoding tail,
the component before it is the basename, everything before that is the directory -- and reports the
size of the directory x tail grid, which is what decides whether a plan is worth running. Writes
nothing.
"""
import collections
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import settings
import snapshot

# `<channelspec>.<quality>.48000.<container>` -- e.g. ln.75.48000.all, lnn.85.48000.all,
# sn.75.48000.english. The channelspec is the only part with letters; the rest are fixed shapes.
TAIL = re.compile(r"\.(?P<chan>[a-z]*n[a-z]*)\.(?P<qual>\d+)\.48000\.(?P<ext>[a-z_]+)$")


def main():
    game = settings.game()
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_asset", set())
    table = "fnv1a_xsounds_v2"

    directories = collections.Counter()
    basenames = collections.Counter()
    tails = collections.Counter()
    dir_tail = collections.defaultdict(set)
    base_dir = collections.defaultdict(set)
    with_tail = 0
    without_tail = 0
    total = 0
    samples = {"with_tail": [], "without_tail": []}

    for line in (Path(settings.tables_csv()) / (table + ".csv")).open(encoding="utf-8"):
        key, sep, display = line.strip().partition(",")
        if not sep:
            continue
        try:
            key = int(key, 16)
        except ValueError:
            continue
        if key & snapshot.ID_MASK not in ids:
            continue
        restored = snapshot.verified_database_row(table, key, display)
        if restored is None:
            continue
        _, name = restored
        if snapshot.fnv1a(name, game, "sound_asset") & snapshot.ID_MASK != key:
            continue
        total += 1
        match = TAIL.search(name)
        if not match:
            without_tail += 1
            if len(samples["without_tail"]) < 12:
                samples["without_tail"].append(name)
            continue
        with_tail += 1
        head = name[: match.start()]
        tail = name[match.start():]
        directory, _, basename = head.rpartition(".")
        directory += "." if directory else ""
        directories[directory] += 1
        basenames[basename] += 1
        tails[tail] += 1
        dir_tail[directory].add(tail)
        base_dir[basename].add(directory)
        if len(samples["with_tail"]) < 6:
            samples["with_tail"].append(name)

    grid = len(directories) * len(tails)
    print(json.dumps({
        "game": game,
        "verified_names": total,
        "with_encoding_tail": with_tail,
        "without_encoding_tail": without_tail,
        "distinct_directories": len(directories),
        "distinct_basenames": len(basenames),
        "distinct_tails": len(tails),
        "observed_dir_x_tail_cells": sum(len(v) for v in dir_tail.values()),
        "dir_x_tail_grid_size": grid,
        "grid_fill_percent": round(100 * sum(len(v) for v in dir_tail.values()) / max(1, grid), 3),
        "distinct_tails_list": [t for t, _ in tails.most_common()],
        "top_directories": directories.most_common(25),
        "top_tails": tails.most_common(20),
        "basenames_seen_in_2plus_directories": sum(1 for v in base_dir.values() if len(v) > 1),
        "samples": samples,
    }, indent=2))


if __name__ == "__main__":
    main()
