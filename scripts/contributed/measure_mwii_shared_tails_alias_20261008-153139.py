"""Where does an MWII sound-*alias* name repeat? The same question asked of the alias pool.

MWII aliases are flat underscore names, not paths -- `wpn_pi_usugar9_fire1_plr_fcg`,
`melee_attack_cloth_piercing_polymer_pri_0_miss_npc` -- so there is no directory axis at all and
the whole-product shape has nothing to hold. What is left is the trailing tokens, which recur across
every weapon: `_fire_plr`, `_sup_npc`, `_reload_empty`.

Two policies differ from the sound-file pool and both matter here:

* aliases hash with the **Treyarch** offset `0xCBF29CE484222325`, not the IW offset the sound
  *files* use, and
* their published keys are **full 64-bit, unmasked**, so about half of them have bit 63 set. A
  comparison that masks to 63 bits silently fails every one of those, which is how a first
  measurement here reported half the pool as "unrestorable" when it was the measurement at fault.

Prints the head/tail support table and what a head x tail product would cost. Writes nothing.
"""
import collections
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import settings
import snapshot

TABLE = "fnv1a_soundbanks_aliases_v2"


def mwii_alias_names(game):
    """Verified alias names the capture holds, compared at full 64 bits as the table stores them."""
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
            # The alias pool is stored at full width, so membership is compared unmasked too.
            if key not in ids and (key & snapshot.ID_MASK) not in ids:
                continue
            restored = snapshot.verified_database_row(TABLE, key, display)
            if restored is None:
                continue
            full, name = restored
            if snapshot.fnv1a(name, game, "sound_alias") != key:
                continue
            yield name


def main():
    game = settings.game()
    heads = collections.Counter()
    support = collections.defaultdict(set)
    counts = collections.Counter()
    names = 0
    widths = collections.Counter()

    for name in mwii_alias_names(game):
        names += 1
        widths[len(name.split("_"))] += 1
        tokens = name.split("_")
        for cut in range(1, len(tokens)):
            head = "_".join(tokens[:cut]) + "_"
            tail = "_".join(tokens[cut:])
            heads[head] += 1
            support[tail].add(head)
            counts[tail] += 1

    print("MWII alias names decomposed : %s" % format(names, ","))
    print("distinct head cuts          : %s" % format(len(heads), ","))
    print("token-count distribution    : %s" % sorted(widths.items()))
    print()
    for threshold in (2, 3, 5, 10, 25, 50):
        kept = [t for t, hs in support.items() if len(hs) >= threshold]
        print("tails attested under >= %3d heads : %s tails, head x tail = %s candidates"
              % (threshold, format(len(kept), ","), format(len(heads) * len(kept), ",")))
    print()
    print("strongest shared tails:")
    for tail, hs in sorted(support.items(), key=lambda kv: -len(kv[1]))[:25]:
        print("  %-42s %4d heads, %5d uses" % (tail, len(hs), counts[tail]))


if __name__ == "__main__":
    main()
