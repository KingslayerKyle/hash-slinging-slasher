"""Every MWII melee-alias grid cell, asked outright.

    python contrib/mwii_melee_grid_plan.py --write-plan plans/mwii_melee.txt
    bin\\windows\\confirm_plan.exe plans/mwii_melee.txt --game MODWAR22 --size

The shared-tail method crossed heads with tails that many heads attest, so its yield sits entirely
where its axis repeats -- 2,729 of the 5,883 alias names it recovered for MWII are `wfoly_plr_*` and
`wfoly_npc_*`, because `npc` and `plr` are attested under 2,928 and 1,945 heads. The melee family is
the largest in the published tables (4,531 of 9,919 rows) and **it recovered not one of them**: a
nine-token name's trailing runs are near-unique, so they never clear the threshold and the family is
skipped whole.

A grid does not need a repeating axis. Every melee alias is one of two fixed shapes, every axis is
read off the published names, and the product is asked rather than inferred:

    melee_<verb>_<armour>_<damage>_<material>_<tier>_<index>_<outcome>_<actor>
    melee_world_<damage>_<material>_<tier>_<index>_<actor>

Measured on the names MWII's own capture and the tables agree on: the first shape is **14,976 cells
of which 4,095 are attested**, and `melee_world` is a second, simpler grid the first pass missed
entirely because it has no outcome axis. Together they are about 18,000 candidates, which is seconds
of machine -- against 137,948 unnamed MWII aliases, of which these two shapes are the single largest
identifiable block.

The two shapes need different endings, so the endings are the union and some combinations are
nonsense (`melee_world_..._0_hit_npc`). At this size nonsense is free: a name that cannot exist
simply does not hash to anything the game holds.
"""
import argparse
import collections
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import settings
import snapshot

ROOT = snapshot.ROOT
TABLE = "fnv1a_soundbanks_aliases_v2"
FULL = re.compile(r"^melee_(?P<verb>[a-z]+)_(?P<armour>[a-z0-9]+)_(?P<damage>[a-z0-9]+)_"
                  r"(?P<material>[a-z0-9]+)_(?P<tier>pri|alt)_(?P<index>\d+)_"
                  r"(?P<outcome>[a-z]+)_(?P<actor>[a-z]+)$")
WORLD = re.compile(r"^melee_world_(?P<damage>[a-z0-9]+)_(?P<material>[a-z0-9]+)_"
                   r"(?P<tier>pri|alt)_(?P<index>\d+)_"
                   r"(?P<actor>[a-z]+)$")


def axes():
    """Every axis value the whole modern alias table attests, not just the target game's.

    A value MWII's *named* names never use can still be a value MWII's *unnamed* ids use -- that is
    the whole reason those ids are unnamed. Costing a few hundred extra candidates to find out.
    """
    found = collections.defaultdict(set)
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
            restored = snapshot.verified_database_row(TABLE, key, display)
            if restored is None:
                continue
            _, name = restored
            match = FULL.match(name)
            if match:
                for axis, value in match.groupdict().items():
                    found[axis].add(value)
                continue
            match = WORLD.match(name)
            if match:
                for axis, value in match.groupdict().items():
                    found[axis].add(value)
    return found


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", default="MODWAR22")
    parser.add_argument("--write-plan", metavar="PATH", required=True)
    options = parser.parse_args(argv)

    found = axes()
    for axis in ("verb", "armour", "damage", "material", "tier", "index", "outcome", "actor"):
        print("%-9s %2d : %s" % (axis, len(found[axis]), " ".join(sorted(found[axis]))),
              file=sys.stderr)

    begins = []
    for verb in sorted(found["verb"]):
        for armour in sorted(found["armour"]):
            for damage in sorted(found["damage"]):
                for material in sorted(found["material"]):
                    begins.append("melee_%s_%s_%s_%s_" % (verb, armour, damage, material))
    for damage in sorted(found["damage"]):
        for material in sorted(found["material"]):
            begins.append("melee_world_%s_%s_" % (damage, material))

    stems = sorted(found["tier"])
    # The union of both shapes' endings. `melee_world` has no outcome axis, so the pairs with one
    # cannot exist -- they cost a few hundred candidates and match nothing.
    ends = set()
    for index in sorted(found["index"]):
        for actor in sorted(found["actor"]):
            ends.add("%s_%s" % (index, actor))
            for outcome in sorted(found["outcome"]):
                ends.add("%s_%s_%s" % (index, outcome, actor))

    begins = sorted(set(begins))
    ends = sorted(ends)
    print("%d beginnings, %d stems, %d endings -> %s candidates"
          % (len(begins), len(stems), len(ends), format(len(begins) * len(stems) * len(ends), ",")),
          file=sys.stderr)

    plan_path = os.path.join(ROOT, options.write_plan)
    base = os.path.splitext(plan_path)[0]
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    written = {}
    for what, entries in (("begins", begins), ("tiers", stems), ("ends", ends)):
        written[what] = base + ".%s.txt" % what
        with open(written[what], "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(entries) + "\n")

    relative = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Written by contrib/mwii_melee_grid_plan.py. Regenerate rather than editing.\n"
            "#\n"
            "# Every melee-alias grid cell, asked outright. The shared-tail method recovers where\n"
            "# its axis repeats -- 2,729 of its 5,883 MWII alias finds are wfoly_plr_*/wfoly_npc_* --\n"
            "# and is blind where it does not, which is why it found none of the largest family in\n"
            "# the tables. A grid needs no repeating axis.\n"
            "#\n"
            "# %d beginnings x %d tiers x %d endings. Axis values are read off the whole modern\n"
            "# alias table, not only the target game's named names: a value MWII's named names never\n"
            "# use can still be a value MWII's unnamed ids use.\n\n"
            % (len(begins), len(stems), len(ends))
        )
        handle.write("label: MWII melee alias grids\n")
        handle.write(
            "describe: every melee armour grid cell -- melee_verb_armour_damage_material_tier_"
            "index_outcome_actor and melee_world_damage_material_tier_index_actor\n\n"
        )
        handle.write("game: %s\n\n" % options.game.upper())
        handle.write("begin: @%s\n\n" % relative(written["begins"]))
        handle.write("stem: @%s\n\n" % relative(written["tiers"]))
        handle.write("end: @%s\n\n" % relative(written["ends"]))
        handle.write("bare: no\n")

    print("\nwrote %s\n\n    bin\\windows\\confirm_plan.exe %s --game %s --size"
          % (relative(plan_path), options.write_plan, options.game.upper()), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))