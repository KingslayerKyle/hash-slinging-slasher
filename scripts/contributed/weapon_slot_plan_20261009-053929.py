"""Weapon-slot plan for the modern games: whatever comes before a weapon x every weapon x whatever
comes after one.

BO7's own images are thick with weapon codes -- `ui_icon_blueprint_sat_ar_finch_spyvil_blueprint_swatch`,
`sat_icon_weapon_sat_sm_otter_material`, `wpn_p13_sh_mbravo_stockpstltube_v0_m1` -- and only ~3% of
the images that exist in BO7 alone are named (19.5k of ~600k, measured 2026-10-09). Slotswap
swaps one token, so it can move `finch` to `albatross` but never `ar_finch` to `sm_otter`; this
treats the whole `<class>_<weapon>` as the slot.

Weapons are every `<codename>_<class>_<name>` seen in any modern name (class in ar sm pi sh lm br
dm sn me la). For every known modern name, each occurrence of a known `<class>_<name>` bounded by
`_`/`/`/start and `_`/end splits it into a beginning (kept with its trailing separator) and an
ending; the plan crosses beginnings x weapons x endings, so a beginning also meets endings it was
never seen with.

    python contrib/weapon_slot_plan.py [--max-begins N --max-ends N]
    confirm_plan contrib/weapon_slot.plan.txt --game BLACKOP7
"""
from pathlib import Path
import argparse
import collections
import re
import sys

ROOT = Path(__file__).resolve().parent
while not (ROOT / "scripts" / "snapshot.py").is_file() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
CONTRIB = ROOT / "contrib"
CLASSES = ("ar", "sm", "pi", "sh", "lm", "br", "dm", "sn", "me", "la")
CODES = ("sat", "t10", "jup", "iw9", "s4", "iw8", "t9", "rex", "s6")
MODERN = ("blackop6", "blackop7", "yamyamok", "modwar22", "modwar7")
KINDS = ("image", "material", "xanim", "sound_alias")
TABLES = ("fnv1a_ximages_v2", "fnv1a_xmaterials_v2", "fnv1a_xanims_v2", "fnv1a_soundbanks_aliases_v2")


def names():
    for t in TABLES:
        f = ROOT / "cod-name-db" / "csv" / (t + ".csv")
        if f.is_file():
            for line in f.open(encoding="utf-8", errors="replace"):
                yield line.rstrip("\r\n").partition(",")[2].lower()
    for top in ("all_names", "findings"):
        for g in MODERN:
            for k in KINDS:
                for f in (ROOT / top / g).rglob(k + "*.txt"):
                    for line in f.open(encoding="utf-8", errors="replace"):
                        yield line.rstrip("\r\n").partition(",")[2].lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-begins", type=int, default=0)
    ap.add_argument("--max-ends", type=int, default=0)
    a = ap.parse_args()
    known = {n for n in names() if n and "~" not in n and "&" not in n and not n.startswith("twc/")}
    wre = re.compile(r"(?:^|[_/])(?:%s)_((?:%s)_[a-z][a-z0-9]+)" % ("|".join(CODES), "|".join(CLASSES)))
    weapons = set()
    for n in known:
        for m in wre.finditer(n):
            weapons.add(m.group(1))
    # Split on every occurrence of a known weapon. Longest weapons first so `ar_mike4` is not
    # matched inside a longer token; boundaries are checked explicitly.
    occ = re.compile(r"(?<![a-z0-9])(%s)(?![a-z0-9])" % "|".join(
        re.escape(w) for w in sorted(weapons, key=len, reverse=True)))
    begins, ends = collections.Counter(), collections.Counter()
    for n in known:
        for m in occ.finditer(n):
            b, e = n[:m.start()], n[m.end():]
            if b and not b.endswith(("_", "/")):
                continue
            if e and not e.startswith("_"):
                continue
            begins[b] += 1
            ends[e] += 1
    bl = [b for b, _ in begins.most_common(a.max_begins or None)]
    el = [e for e, _ in ends.most_common(a.max_ends or None)]
    files = {"weapon_slot_begins.txt": bl, "weapon_slot_weapons.txt": sorted(weapons),
             "weapon_slot_ends.txt": el}
    for f, xs in files.items():
        (CONTRIB / f).write_text("".join(x + "\n" for x in xs if x), encoding="utf-8")
    bare_b = "" in begins
    bare_e = "" in ends
    plan = ["label: weapon-slot plan -- beginnings before a weapon x every weapon x endings after one",
            f"describe: {len(bl)} beginnings, {len(weapons)} <class>_<weapon> codes, {len(el)} endings "
            "measured around every known modern weapon occurrence; see contrib/weapon_slot_plan.py",
            "begin: @contrib/weapon_slot_begins.txt", "stem: @contrib/weapon_slot_weapons.txt",
            "end: @contrib/weapon_slot_ends.txt"]
    (CONTRIB / "weapon_slot.plan.txt").write_text("\n".join(plan) + "\n", encoding="utf-8")
    print(f"weapons {len(weapons)}, begins {len(bl)} (bare {bare_b}), ends {len(el)} (bare {bare_e})",
          file=sys.stderr)


if __name__ == "__main__":
    main()
