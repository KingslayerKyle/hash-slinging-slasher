"""Weapon foley aliases read off the weapon's animations: `sat_vm_ar_condor_inspect_empty_fast02`
-> `fly_plr_ar_condor_inspect_empty_fast02_01..NN` (and fly_npc_, wfoly_plr_, wfoly_npc_).

BO6/BO7 foley is named after the animation it is cut to, then numbered by take; the animations are
~80-85% named and the aliases ~25-30% (2026-10-09), so every animation event is an alias family
whose takes nobody has tried. The weapon-slot plan crosses weapons with alias endings already seen,
which never puts an animation-only event together with a take number.

Stems are `<class>_<weapon>_<event>` from every modern vm/wm animation (codename and vm/wm
stripped) plus the same cut of every known foley alias (take number stripped), so families seen
on either side are extended; endings are bare and `_01`..`_NN`.

    python contrib/anim_to_foley.py --takes 40
    confirm_plan contrib/anim_to_foley.plan.txt --game BLACKOP7
"""
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
MODERN = ("blackop6", "blackop7", "yamyamok", "modwar22", "modwar7")
# Short classes (sat_/t10_/iw9_ weapons) and the long ones BO6-era foley spells out.
CLS = "ar|sm|pi|sh|lm|br|dm|sn|me|la|ww|smg|pistol|lmg|dmr|shotgun|sniper|rifle|launcher|melee|special"
# `sat_vm_ar_condor_...`, `vm_p01_ar_mike4_...`, `p02_ar_...`: codename, view and part are optional.
ANIM = re.compile(r"^(?:[a-z0-9]+_)?(?:(?:vm|wm)_)?(?:[a-z]{0,2}p\d*_)?((?:%s)_[a-z0-9]+_.+)$" % CLS)
FOLEY = re.compile(r"^(?:fly|wfoly|wpn|weap)_(?:(?:rex|sat|jup)_)?(?:(?:plr|npc)_)?((?:%s)_[a-z0-9]+_.+?)(?:_\d{1,3}){0,2}$" % CLS)
BEGINS = ("fly_plr_", "fly_npc_", "wfoly_plr_", "wfoly_npc_", "wpn_", "wfoly_rex_plr_", "wfoly_rex_npc_",
          "wfoly_", "weap_", "fly_sat_", "wfoly_jup_", "fly_")


def rows(kind, table):
    f = ROOT / "cod-name-db" / "csv" / (table + ".csv")
    if f.is_file():
        for line in f.open(encoding="utf-8", errors="replace"):
            yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for g in MODERN:
            for p in (ROOT / top / g).rglob(kind + "*.txt"):
                for line in p.open(encoding="utf-8", errors="replace"):
                    yield line.rstrip("\r\n").partition(",")[2].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--takes", type=int, default=40)
    ap.add_argument("--double", type=int, default=0, help="also _NN_MM takes, MM up to this")
    ap.add_argument("--cross", action="store_true", help="every weapon x every event (anim_to_foley_x.plan.txt)")
    a = ap.parse_args()
    stems = set()
    for n in rows("xanim", "fnv1a_xanims_v2"):
        m = ANIM.match(n)
        if m:
            stems.add(m.group(1))
    na = len(stems)
    for n in rows("sound_alias", "fnv1a_soundbanks_aliases_v2"):
        m = FOLEY.match(n)
        if m:
            stems.add(m.group(1))
    ends = [""] + [f"_{k:02d}" for k in range(1, a.takes + 1)]
    if a.double:
        ends += [f"_{k:02d}_{j:02d}" for k in range(1, 21) for j in range(1, a.double + 1)]
    if a.cross:
        wre = re.compile(r"^((?:%s)_[a-z0-9]+)_(.+)$" % CLS)
        weapons, events = set(), set()
        for st in stems:
            m = wre.match(st)
            if m:
                weapons.add(m.group(1)); events.add("_" + m.group(2))
        nl = chr(10)
        (CONTRIB / "anim_to_foley_x_begins.txt").write_text(
            "".join(b + w + nl for b in BEGINS for w in sorted(weapons)), encoding="utf-8")
        (CONTRIB / "anim_to_foley_x_events.txt").write_text("".join(e + nl for e in sorted(events)), encoding="utf-8")
        (CONTRIB / "anim_to_foley_ends.txt").write_text("".join(e + nl for e in ends if e), encoding="utf-8")
        (CONTRIB / "anim_to_foley_x.plan.txt").write_text(nl.join([
            "label: weapon foley, every weapon x every animation/foley event x take numbers",
            f"describe: {len(BEGINS)} foley prefixes x {len(weapons)} weapons, x {len(events)} events cut from "
            "animations and foley aliases, x bare and take numbers; see contrib/anim_to_foley.py --cross",
            "begin: @contrib/anim_to_foley_x_begins.txt", "stem: @contrib/anim_to_foley_x_events.txt",
            "end: @contrib/anim_to_foley_ends.txt", ""]), encoding="utf-8")
        print(f"cross: {len(weapons)} weapons, {len(events)} events", file=sys.stderr)
        return
    (CONTRIB / "anim_to_foley_stems.txt").write_text("".join(s + "\n" for s in sorted(stems)), encoding="utf-8")
    (CONTRIB / "anim_to_foley_ends.txt").write_text("".join(e + "\n" for e in ends if e), encoding="utf-8")
    (CONTRIB / "anim_to_foley_begins.txt").write_text("".join(b + "\n" for b in BEGINS), encoding="utf-8")
    (CONTRIB / "anim_to_foley.plan.txt").write_text(
        "label: weapon foley aliases from weapon animation events x take numbers\n"
        f"describe: {len(stems)} <class>_<weapon>_<event> stems ({na} from vm/wm animations, the rest from "
        f"known foley aliases) x fly/wfoly plr/npc x bare and _01.._{a.takes:02d}; see contrib/anim_to_foley.py\n"
        "begin: @contrib/anim_to_foley_begins.txt\nstem: @contrib/anim_to_foley_stems.txt\n"
        "end: @contrib/anim_to_foley_ends.txt\n", encoding="utf-8")
    print(f"{len(stems)} stems ({na} from animations)", file=sys.stderr)


if __name__ == "__main__":
    main()
