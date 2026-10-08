r"""Weapon sound aliases: every weapon the *models* name x every event its class's aliases use.

Cold War's weapon aliases are `wpn_<class>_<weapon>_<event...>` (`wpn_smg_accurate_fire_npc`,
`wpn_ar_mobility_act_npc`). Grid fills over the alias pool only see weapons that already have a
named alias; the models name more (`wpn_t9_<class>_<weapon>_...`). This takes the weapons from both,
and offers every one the events seen after any weapon of the same class.

    python contrib/weapon_event_grid.py | bin\windows\confirm_list.exe - --game BLKOPSCW ...
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import token_markov  # noqa: E402

CLASSES = ("ar", "smg", "lmg", "sniper", "shotgun", "pistol", "tr", "launcher", "melee", "special")


def main():
    game = sys.argv[1] if len(sys.argv) > 1 else "BLKOPSCW"
    aliases, _ = token_markov.present(game, "sound_alias")
    models, _ = token_markov.present(game, "xmodel")
    weapons = collections.defaultdict(set)
    events = collections.defaultdict(set)
    for a in aliases:
        t = a.split("_")
        if len(t) >= 4 and t[0] == "wpn" and t[1] in CLASSES:
            weapons[t[1]].add(t[2])
            events[t[1]].add("_".join(t[3:]))
    for m in models:
        t = m.split("_")
        if len(t) >= 4 and t[0] == "wpn" and re.match(r"t\d$", t[1]) and t[2] in CLASSES:
            weapons[t[2]].add(t[3])
    out = set()
    for cls in weapons:
        for w in weapons[cls]:
            for e in events[cls]:
                out.add("wpn_%s_%s_%s" % (cls, w, e))
    out -= aliases
    print("%d candidates" % len(out), file=sys.stderr)
    sys.stdout.write("".join(o + "\n" for o in out))


if __name__ == "__main__":
    main()
