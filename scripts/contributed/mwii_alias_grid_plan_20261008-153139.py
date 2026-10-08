"""MWII sound aliases as `head + shared tail`, asked completely.

    python contrib/mwii_alias_grid_plan.py --write-plan plans/mwii_alias.txt
    bin\\windows\\confirm_plan.exe plans/mwii_alias.txt --game MODWAR22 --size

## The shape of this pool is not the shape of the sound-file pool

MWII aliases are flat underscore names, not paths: `wpn_pi_usugar9_fire1_plr_fcg`,
`melee_attack_nylon_heavy_polymer_pri_2_fatal_npc`. There is no directory axis at all, so the
`directory x basename x tail` product has nothing to hold and `plans/mwii_sound.txt` does not apply
to it. What repeats instead is the trailing token run, and it repeats a great deal:

| tail | attested under |
|---|---:|
| `npc` | 2,928 heads |
| `plr` | 1,945 heads |
| `hit_npc` | 1,024 heads |
| `fatal_npc` | 928 heads |
| `atmo` | 482 heads |

A 2-axis grid shows up directly in the support counts: `0_hit_npc`, `1_hit_npc`, `2_hit_npc` and
`3_hit_npc` are each attested under **exactly 256** heads, which is the `pri_0..3` slot crossed with
a material/polymer pair. Carrying the tails as an axis in their own right is what fills those cells.

## Two policies, both of which fail silently if you get them wrong

* Aliases hash with the **Treyarch** offset `0xCBF29CE484222325`, where sound *files* use the IW
  offset `0x47F5817A5EF961BA`. `games::groups` splits the wanted ids by pool and runs the product
  under each basis, so one plan covers both, but a candidate measured against the wrong one is a
  name that never resolves.
* Alias keys are stored **full 64-bit with no mask**, so roughly half of them have bit 63 set.
  Comparing them at 63 bits fails every one of those and reports a healthy corpus as half missing.

No `end:` column here: an alias name carries no encoding tail. The numeric slots arrive through the
heads, because every cut is carried.
"""
import argparse
import collections
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))

import settings
import snapshot

ROOT = snapshot.ROOT
TABLE = "fnv1a_soundbanks_aliases_v2"


def mwii_alias_names(game):
    """Verified alias names this capture holds, compared at the full 64 bits the table stores."""
    path = [p for p in snapshot.snapshots() if snapshot.read(p).game == game][0]
    held = {k: set(v) for k, v in snapshot.read(path).by_pool().items()}
    ids = held.get("sound_alias", set())
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
            yield name


def vocabulary(game, min_heads):
    heads = collections.Counter()
    support = collections.defaultdict(set)
    names = 0
    for name in mwii_alias_names(game):
        tokens = name.split("_")
        if len(tokens) < 2:
            continue
        names += 1
        for cut in range(1, len(tokens)):
            heads["_".join(tokens[:cut]) + "_"] += 1
            tail = "_".join(tokens[cut:])
            support[tail].add("_".join(tokens[:cut]) + "_")
    carried = sorted(t for t, hs in support.items() if len(hs) >= min_heads)
    return heads, carried, names


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--game", default="MODWAR22")
    parser.add_argument("--min-heads", type=int, default=2,
                        help="how many heads a tail must be attested under to be carried")
    parser.add_argument("--write-plan", metavar="PATH", required=True)
    options = parser.parse_args(argv)

    game = options.game.upper()
    heads, carried, names = vocabulary(game, options.min_heads)
    print("alias names decomposed %s -> %s heads, %s shared tails (>=%d heads)"
          % (format(names, ","), format(len(heads), ","), format(len(carried), ","),
             options.min_heads), file=sys.stderr)

    plan_path = os.path.join(ROOT, options.write_plan)
    base = os.path.splitext(plan_path)[0]
    os.makedirs(os.path.dirname(plan_path), exist_ok=True)
    written = {}
    for what, entries in (("heads", sorted(heads)), ("tails", carried)):
        written[what] = base + ".%s.txt" % what
        with open(written[what], "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(entries) + "\n")

    relative = lambda path: os.path.relpath(path, ROOT).replace("\\", "/")
    with open(plan_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(
            "# Written by contrib/mwii_alias_grid_plan.py. Regenerate rather than editing.\n"
            "#\n"
            "# MWII aliases are flat underscore names, so there is no directory axis and the\n"
            "# directory x basename x tail product does not apply. The repetition is in the trailing\n"
            "# token run: npc under 2,928 heads, hit_npc under 1,024, fatal_npc under 928, and\n"
            "# pri_0..3 crossed with a material pair showing up as four tails each under 256 heads.\n"
            "#\n"
            "# Heads are carried at EVERY underscore cut, so numeric slots arrive as heads and the\n"
            "# correct (head, tail) pairing is always in the product.\n"
            "# %s heads x %s shared tails.\n\n"
            % (format(len(heads), ","), format(len(carried), ","))
        )
        handle.write("label: MWII sound alias heads x shared tails\n")
        handle.write(
            "describe: every measured MWII alias head crossed with every trailing token run "
            "attested under two or more heads\n\n"
        )
        handle.write("game: %s\n\n" % game)
        handle.write("begin: @%s\n\n" % relative(written["heads"]))
        handle.write("stem: @%s\n\n" % relative(written["tails"]))
        handle.write("bare: no\n")

    print("\nwrote %s\n\n    bin\\windows\\confirm_plan.exe %s --game %s --size"
          % (relative(plan_path), options.write_plan, game), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))