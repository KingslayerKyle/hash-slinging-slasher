"""The MWII melee armour grid, enumerated rather than inferred.

## Why this family, and why the shared-tail method never touched it

Of the 5,883 alias names this project recovered for MWII, **2,729 are `wfoly_plr_*` and `wfoly_npc_*`
and not one is `melee_*`** -- while `melee_attack_*` and `melee_character_*` together are the single
largest family in the published alias tables, 4,531 of 9,919 rows.

The reason is a property of the method, not of the family. `mwii_alias_grid_plan.py` crosses heads
with *shared* tails, carrying a tail only where many heads attest it, and yield tracks tail support
exactly: `npc` is attested under 2,928 heads, `plr` under 1,945, so `wfoly_*` explodes. The melee
names are nine tokens long and their trailing runs are near-unique, so they almost never clear the
threshold and the family is skipped wholesale. **A method's yield is concentrated wherever its axis
repeats, and it is blind exactly where the axis does not.**

## The shape

Every melee alias is the same eight-axis grid:

    melee_ <verb>_<armourclass>_<damage>_<armourtype>_<pri|alt>_<n>_<hit|fatal|miss>_<npc|plr>

So it is not text and does not need to be guessed at: every axis is read off the published names,
every value is measured rather than assumed, and the product is asked outright. Four armour classes
x fifteen damage types x three armour types x two verbs x two tiers x four indices x three outcomes
x two actors is **34,560 cells against 4,531 named** -- and asking all of them costs seconds, because
unlike the sound files there is no path and no encoding tail to carry.

Prints each axis with its measured vocabulary, the product size, and how many cells are already
attested. Writes nothing; `mwii_melee_grid_plan.py` writes the plan.
"""
import collections
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import settings
import snapshot

TABLE = "fnv1a_soundbanks_aliases_v2"
SHAPE = re.compile(r"^melee_(?P<verb>[a-z]+)_(?P<armour>[a-z0-9]+)_(?P<damage>[a-z0-9]+)_"
                   r"(?P<material>[a-z0-9]+)_(?P<tier>pri|alt)_(?P<index>\d+)_"
                   r"(?P<outcome>[a-z]+)_(?P<actor>[a-z]+)$")


def main():
    game = settings.game()
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_alias", set())

    axes = collections.defaultdict(collections.Counter)
    cells = set()
    total = 0
    unmatched = collections.Counter()

    with (Path(settings.tables_csv()) / (TABLE + ".csv")).open(encoding="utf-8",
                                                               errors="replace") as handle:
        for line in handle:
            key, sep, display = line.strip().partition(",")
            if not sep:
                continue
            try:
                key = int(key, 16)
            except ValueError:
                continue
            if key not in ids and (key & snapshot.ID_MASK) not in ids:
                continue
            restored = snapshot.verified_database_row(TABLE, key, display)
            if restored is None:
                continue
            _, name = restored
            if snapshot.fnv1a(name, game, "sound_alias") != key:
                continue
            if not name.startswith("melee_"):
                continue
            total += 1
            match = SHAPE.match(name)
            if not match:
                unmatched[name] += 1
                continue
            for axis, value in match.groupdict().items():
                axes[axis][value] += 1
            cells.add(name)

    product = 1
    report = {}
    for axis in ("verb", "armour", "damage", "material", "tier", "index", "outcome", "actor"):
        values = sorted(axes[axis])
        product *= len(values)
        report[axis] = {"count": len(values), "values": values}
        print("%-9s %2d values: %s" % (axis, len(values), " ".join(values)))

    print()
    print("melee names matching the 8-axis shape : %s of %s" % (format(len(cells), ","), total))
    print("distinct attested cells               : %s" % format(len(cells), ","))
    print("full grid product                     : %s" % format(product, ","))
    print("cells the grid would add              : %s"
          % format(max(0, product - len(cells)), ","))
    if unmatched:
        print("\n%d melee name(s) the shape does not fit -- these matter, they are not in the grid:"
              % len(unmatched))
        for name in list(unmatched)[:20]:
            print("  %s" % name)


if __name__ == "__main__":
    main()