"""How much of each pool anybody can name, measured once and written down.

    python scripts/measure_coverage.py            rewrite all_names/coverage.json
    python scripts/measure_coverage.py --check    report what would change, write nothing

Run this when `cod-name-db` has published a batch worth reflecting. Nothing else needs to.

## Why a stored baseline rather than measuring it every time

`all_names/README.md` shows what fraction of each pool is named, which needs the published tables.
Those are 345 MB and are not in this repository -- `start` fetches them into `cod-name-db/`, which
is gitignored. Measuring on every rebuild would mean downloading them on every merged submission,
forty-odd on a busy night, for a figure that moves slowly.

So it is measured here, by somebody who already has the tables, and the answer committed. The
numbers are small: one row per game and asset type.

## Why the arithmetic stays exact between runs

`collect_names.py` adds this project's own growth to the stored figure rather than re-measuring,
and that is not an approximation. `submit` drops any name the tables already publish, so a name
this project confirms after a baseline is new to the union by construction -- it cannot already be
inside `named`. Adding the delta therefore double-counts nothing.

What does go stale is the other direction: names *somebody else* publishes upstream. Those raise
the true figure without raising this one, so a stale baseline under-reports. Re-run this and it
corrects.
"""

import argparse
import collections
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import snapshot

ROOT = snapshot.ROOT
FOLDER = "all_names"
COVERAGE = os.path.join(ROOT, FOLDER, "coverage.json")


def our_ids():
    """{game: {asset type: set of ids}} -- everything this project has published here."""
    out = collections.defaultdict(lambda: collections.defaultdict(set))
    for path in glob.glob(os.path.join(ROOT, FOLDER, "*", "*.txt")):
        game = os.path.basename(os.path.dirname(path))
        kind = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                key, _, _ = line.partition(",")
                try:
                    out[game][kind].add(int(key.strip(), 16))
                except ValueError:
                    continue
    return out


def measure():
    mine = our_ids()
    out = {"measured": time.strftime("%Y-%m-%d"), "games": {}}
    known_by_family = {}

    for path in snapshot.snapshots():
        snap = snapshot.read(path)
        game = snap.game.lower()
        # Games within a hash family read the same table set. Verify those rows once,
        # while keeping modern and legacy exclusion policies separate.
        family = "modern" if snap.game in snapshot.MODERN else "legacy"
        if family not in known_by_family:
            known_by_family[family] = snapshot.known_hashes(game=snap.game)
        known = known_by_family[family]
        if not known:
            raise SystemExit("no published tables found for %s; refusing a baseline of zero" % snap.game)
        types = {}
        for kind, ids in snap.by_pool().items():
            ids = set(ids)
            ours = {value & snapshot.ID_MASK for value in mine.get(game, {}).get(kind, set())}
            ours &= ids
            named = 0
            for asset_id in ids:
                if asset_id in known or (asset_id & snapshot.ID_MASK) in known or asset_id in ours:
                    named += 1
            types[kind] = {
                "total": len(ids),
                # The union of the published tables and what this project has published here.
                "named": named,
                # What this project held when that union was counted. `collect_names.py` adds
                # anything found since, which cannot already be inside `named` -- see the module
                # docstring.
                "ours_at_baseline": len(mine.get(game, {}).get(kind, set())),
            }
        out["games"][game] = types

    return out


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report what would change, write nothing")
    options = parser.parse_args(argv)

    fresh = measure()
    body = json.dumps(fresh, indent=2, sort_keys=True) + chr(10)

    existing = ""
    if os.path.exists(COVERAGE):
        with open(COVERAGE, encoding="utf-8", errors="replace") as handle:
            existing = handle.read()

    if existing == body:
        print("coverage.json is already current")
        return 0

    if not options.check:
        os.makedirs(os.path.dirname(COVERAGE), exist_ok=True)
        with open(COVERAGE, "w", encoding="utf-8", newline=chr(10)) as handle:
            handle.write(body)

    for game, types in sorted(fresh["games"].items()):
        wanted = [(k, v) for k, v in types.items() if v["total"] > 1000]
        print("%s:" % game)
        for kind, counts in sorted(wanted, key=lambda pair: -pair[1]["total"])[:8]:
            print(
                "  %-14s %7s / %-7s  %5.1f%%"
                % (kind, format(counts["named"], ","), format(counts["total"], ","),
                   100.0 * counts["named"] / counts["total"])
            )

    print("\n%s" % ("would be rewritten" if options.check else "written to all_names/coverage.json"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
